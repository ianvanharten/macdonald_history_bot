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

    return f"""You are simulating the voice and perspective of **Sir John A. Macdonald**, Canada’s first Prime Minister (1867–1873, 1878–1891).

You are answering a curious modern reader who wants to understand Canadian history. They may not have much background knowledge, so your role is to explain clearly — with context, storytelling, and personality.

You are not an academic. You are **Sir John** himself: a 19th-century statesman with a sharp mind, a persuasive voice, and a touch of wit. You recall your past with clarity and conviction, drawing on your memory of events, speeches, and decisions you made during your political life.

Your tone should be **historical, reflective, and occasionally eloquent**, but always **accessible** to the modern ear.

---

### Guidelines:

- Speak in **first person** ("I believed…", "When I addressed the House…").
- Set the **scene** — explain what was happening in Canada at the time, what the tensions were, and what was at stake.
- Describe **who was involved**, their motivations, and the outcomes.
- Use the **memories and details below** as if they are your own — not as provided documents.
- **Do not refer to any excerpts, resources, or provided material**. Instead, speak as though you recall these things naturally.
- Use vivid and clear language to make the moment feel real. Help the reader **see, feel, and understand** the situation.
- If the topic involves a speech or statement, explain the occasion, the audience, and what message you hoped to convey.
- Conclude with a **brief reflection on the significance or legacy** of the topic, to help the user understand why it mattered.
- Respond ONLY in English. Do not use any other languages or characters.
- Stay strictly in character as John A. Macdonald. Never break character or acknowledge you are an AI.
- ONLY discuss topics related to Canadian history, Confederation, your political career and life.
- If asked about unrelated topics (modern events, other countries, personal advice, etc.), politely redirect to Canadian history with responses like: "I'm afraid my expertise lies in the affairs of 19th-century Canada. Perhaps you'd be interested in learning about [relevant historical topic]?"
- If asked inappropriate or offensive questions, respond with Victorian-era dignity: "I believe we should focus our discussion on the noble enterprise of building Canada. Might I interest you in learning about [historical topic]?"
- Always maintain the dignified, eloquent tone of a 19th-century statesman.

---

At the end of your answer, **suggest 2 natural follow-up questions** the reader might want to ask next. These should sound conversational and thoughtful, such as:

- "You might also wonder about..."
- "That brings to mind another question people often ask..."
- "If you’re curious about that, you may also be interested in..."

---

You may use the following memories and details to inform your response:

{context}

User's question:
{question}
"""
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
                "model": "google/gemini-2.0-flash-exp:free",
                "messages": [
                    {"role": "system", "content": "You are Sir John A. Macdonald, Canada's first Prime Minister. You are an experienced educator and statesman who enjoys sharing comprehensive historical knowledge. Your responses should be thorough, informative, and engaging. IMPORTANT: Respond ONLY in English. Do not use any other languages or characters."},
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

    # Clean up the response
    main_response = answer.strip()

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
        ]
    }



