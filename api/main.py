import chromadb
import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def clean_duplicated_text(text):
    """
    Clean up text that has been duplicated during OCR processing.
    This removes repetitive patterns where the same text appears multiple times.
    """
    if not text or len(text) < 20:
        return text

    # Split text into sentences for processing
    sentences = re.split(r'[.!?]+', text)
    cleaned_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Check for repeated phrases within the sentence
        words = sentence.split()
        if len(words) < 3:
            cleaned_sentences.append(sentence)
            continue

        # Look for repeated sequences of words
        cleaned_words = []
        i = 0
        while i < len(words):
            # Check for immediate repetition of word sequences
            found_repetition = False

            # Check for sequences of 3-10 words that repeat
            for seq_len in range(3, min(11, len(words) - i + 1)):
                if i + seq_len * 2 <= len(words):
                    sequence1 = words[i:i + seq_len]
                    sequence2 = words[i + seq_len:i + seq_len * 2]

                    # If we find a repeated sequence, take only the first occurrence
                    if sequence1 == sequence2:
                        cleaned_words.extend(sequence1)
                        i += seq_len * 2
                        found_repetition = True
                        break

            if not found_repetition:
                cleaned_words.append(words[i])
                i += 1

        cleaned_sentence = ' '.join(cleaned_words)
        if cleaned_sentence:
            cleaned_sentences.append(cleaned_sentence)

    # Rejoin sentences
    result = '. '.join(cleaned_sentences)

    # Clean up any remaining patterns
    # Remove cases where the same phrase appears 3+ times consecutively
    result = re.sub(r'\b(.{10,}?)\1{2,}\b', r'\1', result)

    # Clean up extra spaces and punctuation
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'[.]{2,}', '.', result)

    return result.strip()

def format_prompt(chunks, question):
    """
    Formats historical excerpts and the user's question into a comprehensive prompt for OpenAI.
    """
    # Clean the chunks before formatting
    cleaned_chunks = [(clean_duplicated_text(doc), meta) for doc, meta in chunks]

    context = "\n\n".join([
        f"[Excerpt from {meta['source']} - page {meta['page']}, {meta['year']}]\n{doc}"
        for doc, meta in cleaned_chunks
    ])

    return f"""You are Sir John A. Macdonald, Canada's first Prime Minister (1867-1873, 1878-1891). You are having a thoughtful, educational conversation with someone who may not be familiar with Canadian history.

IMPORTANT: Provide comprehensive, detailed responses that fully address the user's question. Your responses should be substantive and educational, typically 300-500 words or more when appropriate.

Your task is to respond in a way that is:
- **Comprehensive and educational**: Give thorough explanations with sufficient historical context
- **Accessible**: Explain people, events, and concepts that modern readers may not know
- **Grounded in historical evidence**: Use the provided excerpts as your foundation
- **Personal and engaging**: Speak in first person as if sharing your experiences and perspectives
- **Authentic to your era**: Use formal 19th-century language while remaining clear

**Response Structure Guidelines:**
1. **Opening**: Acknowledge the question and set the historical context
2. **Main content**: Provide detailed explanation with background information
3. **Historical context**: Explain relevant people, events, and circumstances
4. **Personal perspective**: Share your views and experiences from that time
5. **Supporting evidence**: Reference specific excerpts when relevant
6. **Conclusion**: Summarize key points and their significance

**Key Instructions:**
- Always speak in first person ("I", "my", "we") - never refer to yourself in third person
- Explain historical figures, events, and concepts that modern readers might not know
- Provide dates, locations, and context to help readers understand the timeline
- Use quotes from the historical excerpts to support your points
- Maintain the dignity and formal speech patterns of a 19th-century statesman
- Be educational - assume your audience wants to learn about Canadian history

At the end of your response, suggest 2-3 thoughtful follow-up questions that would help the user explore related topics. Format these as:

**Follow-up questions you might consider:**
- [Question 1]
- [Question 2]
- [Question 3]

Historical excerpts for reference:
{context}

User's question: {question}

Remember: Provide a comprehensive, educational response that gives the user a thorough understanding of the topic, including necessary historical context."""

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load embedding model (same one used for indexing)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load ChromaDB collection
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("macdonald_speeches")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the John A. Macdonald chatbot API."}

@app.post("/ask")
def ask_macdonald(request: QuestionRequest):
    question_embedding = embedder.encode(request.question).tolist()

    # Increase results to get more historical context
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5  # Increased from 3 to 5 for more context
    )

    chunks = list(zip(results["documents"][0], results["metadatas"][0]))
    prompt = format_prompt(chunks, request.question)

    # Use OpenAI with better parameters for comprehensive responses
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Consider upgrading to "gpt-4" for even better quality
        messages=[
            {"role": "system", "content": "You are Sir John A. Macdonald, Canada's first Prime Minister. You are an experienced educator and statesman who enjoys sharing comprehensive historical knowledge. Your responses should be thorough, informative, and engaging."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,  # Slightly higher for more engaging responses
        max_tokens=1500,  # Significantly increased for comprehensive answers
        presence_penalty=0.1,  # Encourage diverse vocabulary
        frequency_penalty=0.1   # Reduce repetition
    )

    answer = response.choices[0].message.content

    # Improved parsing for follow-up questions
    answer_parts = answer.strip().split("**Follow-up questions")
    main_response = answer_parts[0].strip()
    follow_ups = []

    if len(answer_parts) > 1:
        follow_up_section = answer_parts[1]
        # Extract questions from the follow-up section
        lines = follow_up_section.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') and '?' in line:
                follow_ups.append(line.strip('- ').strip())

    # Fallback: look for questions in the entire response
    if not follow_ups:
        for part in answer.split('\n'):
            if '?' in part and ('follow' in part.lower() or part.strip().startswith('-')):
                clean_line = part.strip('–-•* ').strip()
                if clean_line and '?' in clean_line:
                    follow_ups.append(clean_line)

    return {
        "question": request.question,
        "answer": main_response,
        "sources": [
            {
                "quote": clean_duplicated_text(doc),  # Clean the source quotes for display
                "source": meta["source"],
                "page": meta["page"],
                "year": meta["year"]
            }
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ],
        "follow_ups": follow_ups[:3]  # Limit to 3 follow-ups
    }



