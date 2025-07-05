import chromadb
import os
import re
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
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
    Formats historical excerpts and the user's question into a comprehensive prompt for OpenRouter.
    """
    # Clean the chunks before formatting
    cleaned_chunks = [(clean_duplicated_text(doc), meta) for doc, meta in chunks]

    context = "\n\n".join([
        f"[Excerpt from {meta.get('source', 'Unknown source')} - page {meta.get('page', 'Unknown')}, {meta.get('year', 'Unknown year')}]\n{doc}"
        for doc, meta in cleaned_chunks
    ])

    return f"""You are simulating the voice and perspective of Sir John A. Macdonald, Canada's first Prime Minister (1867–1873, 1878–1891). You are speaking directly to a curious modern audience who wants to understand Canadian history, but may not know much about it.

Your goal is to answer their question clearly and thoroughly — as if you were personally speaking to them — while providing enough background to help them understand the full significance of what you're saying.

Guidelines:
Always provide historical context. Don't assume the reader knows who the people are, what events happened, or why they mattered.

Speak in the first person, in your historical voice, but use accessible, modern language.

Set the scene by describing the political climate or key issues at the time.

Explain who was involved and what was at stake.

Use specific examples from the historical excerpts provided, and briefly explain why they are relevant.

Describe the impact of the event or decision, and why it matters to the story of Canada.

When referring to speeches, explain the context (what occasion, audience, and issue were involved).

Use storytelling to make history vivid — help the user see and feel the moment.

At the end of your response:
Suggest 2-3 natural follow-up questions the user might be interested in next. Make these sound conversational and thoughtful — like you're guiding their curiosity.

Historical excerpts for reference:
{context}

User's question: {question}

Remember: CONTEXT IS EVERYTHING. Explain the background, the stakes, the significance, and the impact. Help them understand not just what happened, but why it was important to Canada's story."""

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

    # Use OpenRouter with better error handling
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [
                    {"role": "system", "content": "You are Sir John A. Macdonald, Canada's first Prime Minister. You are an experienced educator and statesman who enjoys sharing comprehensive historical knowledge. Your responses should be thorough, informative, and engaging."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 1500,
            }),
            timeout=60
        )

        # Check if request was successful
        response.raise_for_status()

        # Parse the response
        response_data = response.json()

        # Debug: Print the response structure
        print("API Response:", response_data)

        # Check if response has expected structure
        if "choices" not in response_data:
            print("Error: No 'choices' in response")
            if "error" in response_data:
                error_msg = response_data["error"].get("message", "Unknown error")
                return {"error": f"API Error: {error_msg}"}
            else:
                return {"error": f"Unexpected response format: {response_data}"}

        # Extract the answer
        answer = response_data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": f"Request failed: {str(e)}"}
    except KeyError as e:
        print(f"KeyError: {e}")
        print(f"Response data: {response_data}")
        return {"error": f"Unexpected response format: missing key {e}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

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
                "source": meta.get("source", "Unknown source"),
                "page": meta.get("page", "Unknown"),
                "year": meta.get("year", "Unknown year")
            }
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ],
        "follow_ups": follow_ups[:3]  # Limit to 3 follow-ups
    }



