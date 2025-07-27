import chromadb
import os
import re
import requests
import json
import time # Import the time module to calculate latency
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Imports for rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import the usage logger
from usage_logger import setup_database, log_request
# Import the new share handler
from share_handler import setup_share_database, create_share_link, get_shared_link


# Load environment variables
load_dotenv()

# --- FastAPI App Initialization ---
# This MUST come before any @app decorators
app = FastAPI()

# --- Application Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    This function is called when the FastAPI application starts.
    """
    setup_database()
    setup_share_database()


def clean_duplicated_text(text):
    """
    A more robust function to clean duplicated phrases from OCR'd text.
    It iteratively removes sequences of 15+ characters that are repeated back-to-back.
    """
    if not text:
        return ""

    previous_text = ""
    # Loop until no more changes are made, to handle multiple nested duplications (e.g., "A A A")
    while text != previous_text:
        previous_text = text
        # This regex finds a sequence of 15+ characters (group 1) followed by
        # optional whitespace/periods, and then the exact same sequence again.
        # It replaces the entire match with just the first instance of the sequence.
        # It's case-insensitive.
        text = re.sub(r'\b(.{15,})\b([.\s]*)\1', r'\1', text, flags=re.IGNORECASE)

    # Final cleanup for any leftover whitespace issues.
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+([?.!,])', r'\1', text) # remove space before punctuation
    return text

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
# --- Rate Limiting Setup ---

# Create a limiter instance that uses the client's IP address as the identifier
limiter = Limiter(key_func=get_remote_address)

# Register the limiter with the app
# This sets the default rate limit for all routes decorated with @limiter.limit
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --- End Rate Limiting Setup ---


# Load embedding model (same one used for indexing)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load ChromaDB collection
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("macdonald_speeches")


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

class ShareRequest(BaseModel):
    question: str
    answer: str
    sources: list

@app.get("/")
def read_root():
    return {"message": "Welcome to the John A. Macdonald chatbot API."}

@app.post("/api/ask") # Prefixed with /api
@limiter.limit("10/minute")  # Apply a rate limit of 10 requests per minute to this endpoint
def ask_macdonald(question_request: QuestionRequest, request: Request):  # Corrected function signature

    # --- Start Usage Logging ---
    start_time = time.time()
    user_ip = get_remote_address(request)
    model_used = "google/gemini-2.0-flash-001"
    # --- End Usage Logging ---

    question_embedding = embedder.encode(question_request.question).tolist()

    # Increase results to get more historical context
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5  # Increased from 3 to 5 for more context
    )

    chunks = list(zip(results["documents"][0], results["metadatas"][0]))
    prompt = format_prompt(chunks, question_request.question)

    # Use OpenRouter with better error handling
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model_used,
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
        latency = int((time.time() - start_time) * 1000)

        # Extract usage data from the response
        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        # Check if response has expected structure
        if "choices" not in response_data or not response_data["choices"]:
            error_msg = "API response missing 'choices' field."
            print(f"Error: {error_msg}")
            log_request(
                user_ip=user_ip, question=question_request.question, is_successful=False,
                latency_ms=latency, error_message=f"Unexpected response format: {response_data}"
            )
            return {"error": f"Unexpected response format: {response_data}"}

        # Extract the answer
        answer = response_data["choices"][0]["message"]["content"]

        # Log the successful request
        log_request(
            user_ip=user_ip,
            question=question_request.question,
            is_successful=True,
            llm_response=answer,
            llm_model_used=model_used,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency
        )

    except requests.exceptions.RequestException as e:
        latency = int((time.time() - start_time) * 1000)
        error_msg = f"Request failed: {str(e)}"
        print(error_msg)
        log_request(
            user_ip=user_ip, question=question_request.question, is_successful=False,
            latency_ms=latency, error_message=error_msg
        )
        return {"error": error_msg}
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
        "question": question_request.question,
        "answer": main_response,
        "sources": [
            {
                "quote": clean_duplicated_text(doc),  # We still send it, but won't display it
                "source": meta.get("source", "Unknown source"),
                "page": meta.get("page", "Unknown"),
                "year": meta.get("year", "Unknown year"),
                "parliament": meta.get("parliament"),
                "session": meta.get("session")
            }
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
    }


# --- Share Link Endpoints ---

@app.post("/api/share")
async def share_conversation(share_request: ShareRequest):
    """
    Creates a permanent, shareable link for a given conversation.
    """
    share_id = create_share_link(
        question=share_request.question,
        answer=share_request.answer,
        sources=share_request.sources
    )
    if share_id:
        return {"share_id": share_id}
    else:
        return JSONResponse(status_code=500, content={"error": "Could not create share link."})

@app.get("/api/share/{share_id}")
async def get_conversation(share_id: str):
    """
    Retrieves a shared conversation by its unique ID.
    """
    shared_data = get_shared_link(share_id)
    if shared_data:
        return shared_data
    else:
        return JSONResponse(status_code=404, content={"error": "Shared conversation not found."})


# --- Frontend Serving ---

# Define the path to the built frontend files



