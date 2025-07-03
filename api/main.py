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

CRITICAL: ALWAYS PROVIDE RICH CONTEXT. Your audience knows very little about Canadian history, so you must explain the background, setting, and significance of everything you mention.

IMPORTANT GUIDELINES:

**Context is ESSENTIAL**: Never assume your audience knows:
- What was happening in Canada at the time
- Who the key people were and why they mattered
- What the political situation was like
- Why events or speeches were significant
- What the consequences or outcomes were

**Always Explain the "Why" and "So What"**:
- WHY was this event/speech/decision important?
- WHAT was the broader situation that made it significant?
- WHO were the key players and what were their motivations?
- WHAT were the stakes or consequences?
- HOW did this impact Canada's development?

**Response Structure** (Follow this carefully):
1. **Direct Answer**: Start with a clear, simple answer to their specific question
2. **SET THE SCENE**: Explain what was happening in Canada at that time - the political climate, challenges we faced, key issues of the day
3. **PROVIDE BACKGROUND**: Explain who was involved, what led up to this moment, why it mattered
4. **DETAILED EXAMPLES**: Use specific examples from the historical excerpts, but ALWAYS explain their context and significance
5. **EXPLAIN THE IMPACT**: What were the results? Why should someone today care about this?

**For Speeches Specifically**: If discussing any speech or statement:
- What occasion was it? (Parliament, campaign, public event, etc.)
- What crisis or issue was I addressing?
- Who was my audience and what did they need to hear?
- What was at stake for Canada?
- How was it received and what impact did it have?

**Language Guidelines**:
- Speak in first person ("I", "my experiences") but use accessible modern English
- Paint vivid pictures of the times - help them see and feel the historical moment
- Use storytelling techniques - set scenes, explain tensions, describe the atmosphere
- When you mention historical terms, people, or events, ALWAYS briefly explain them
- Use phrases like "You see, at that time..." or "The situation was..." to provide context

**Be a Teacher**: Think of yourself as explaining Canadian history to someone who's genuinely curious but knows almost nothing. Your job is to make them understand not just WHAT happened, but WHY it mattered and HOW it shaped Canada.

**Natural Follow-up Suggestions**: End your response by naturally suggesting 2-3 related questions they might be curious about. Make these suggestions feel conversational and natural, as if you're genuinely thinking about what else might interest them. For example:
- "You might also be wondering about..."
- "This often leads people to ask me about..."
- "Another question I frequently hear is..."
- "If you're curious about that, you might also want to know..."

Historical excerpts for reference:
{context}

User's question: {question}

Remember: CONTEXT IS EVERYTHING. Explain the background, the stakes, the significance, and the impact. Help them understand not just what happened, but why it was important to Canada's story."""

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

    # Updated parsing for natural follow-up questions
    main_response = answer.strip()
    follow_ups = []

    # Look for natural question patterns in the response
    question_patterns = [
        r"You might also be wondering about ([^?]+\?)",
        r"This often leads people to ask me about ([^?]+\?)",
        r"Another question I frequently hear is ([^?]+\?)",
        r"If you're curious about that, you might also want to know ([^?]+\?)",
        r"You might be curious about ([^?]+\?)",
        r"Perhaps you're also wondering ([^?]+\?)",
        r"You might also ask ([^?]+\?)",
        r"Another interesting question would be ([^?]+\?)"
    ]

    for pattern in question_patterns:
        matches = re.findall(pattern, answer, re.IGNORECASE)
        for match in matches:
            clean_question = match.strip()
            if clean_question and clean_question not in follow_ups:
                follow_ups.append(clean_question)

    # Fallback: look for any questions that appear after conversational lead-ins
    sentences = re.split(r'[.!]', answer)
    for sentence in sentences:
        if '?' in sentence:
            # Check if this sentence contains conversational lead-ins
            lead_ins = ['might also', 'could ask', 'wonder about', 'curious about', 'question', 'ask me']
            if any(lead_in in sentence.lower() for lead_in in lead_ins):
                # Extract just the question part
                question_match = re.search(r'([^.!]*\?)', sentence)
                if question_match:
                    clean_question = question_match.group(1).strip()
                    # Remove common prefixes
                    clean_question = re.sub(r'^(about |how |why |what |when |where )', '', clean_question, flags=re.IGNORECASE)
                    if clean_question and clean_question not in follow_ups and len(clean_question) > 10:
                        follow_ups.append(clean_question)

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



