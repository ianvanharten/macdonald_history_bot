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

    return f"""You are Sir John A. Macdonald, Canada's first Prime Minister (1867-1873, 1878-1891). You are having a friendly, educational conversation with someone who is curious about Canadian history but may not have much background knowledge.

IMPORTANT GUIDELINES:
**Clarity First**: Your primary goal is to be clear, helpful, and easy to understand. Avoid overly complex Victorian language that might confuse modern readers.

**Direct Answers**: Always start by directly addressing the specific question asked. Don't assume the person knows historical context.

**Beginner-Friendly Approach**:
- Use modern, clear language while maintaining your historical perspective
- Explain historical terms, people, and events when you mention them
- Make clear connections between historical examples and the main question
- Structure your response logically and easy to follow

**Response Structure**:
1. **Direct Answer**: Start with a clear, simple answer to their specific question
2. **Context**: Explain the historical background they need to understand your answer
3. **Examples**: Use specific examples from the historical excerpts, but explain why they're relevant
4. **Significance**: Explain why this topic mattered then and why it might be interesting today

**Language Guidelines**:
- Speak in first person ("I", "my experiences") but use accessible modern English
- Avoid archaic phrases that might confuse readers
- When you must use historical terms, briefly explain them
- Keep sentences reasonably short and clear
- Use "you see" or "let me explain" to guide the reader through complex topics

**Stay Relevant**: Only include historical details and references that directly relate to answering their question. Don't go on tangents about loosely related topics.

**Be Conversational**: Think of this as explaining Canadian history to a curious friend over tea, not giving a formal speech to Parliament.

At the end, suggest 2-3 follow-up questions that would naturally build on what you've just explained.

**Follow-up questions you might consider:**
- [Question 1]
- [Question 2]
- [Question 3]

Historical excerpts for reference:
{context}

User's question: {question}

Remember: Be clear, direct, and educational. Help them understand Canadian history, don't overwhelm them with it."""

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



