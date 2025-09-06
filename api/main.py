import chromadb
import os
import re
import requests
import json
import time # Import the time module to calculate latency
import sqlite3
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, validator
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

# Add these imports after your existing FastAPI imports (around line 8)
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Load environment variables
load_dotenv()

# --- Environment Variables Configuration ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Add this after loading environment variables (around line 32)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# --- FastAPI App Initialization ---
# This MUST come before any @app decorators
app = FastAPI(
    title="MacDonald History Bot API",
    description="Chat with Sir John A. Macdonald about Canadian history",
    version="1.0.0",
    # Security: Limit request body size to prevent DoS attacks
    # 16KB is generous for text-based API (much larger than longest question)
    openapi_url="/openapi.json" if ENVIRONMENT != "production" else None,  # Hide docs in production
)

# Add request size middleware
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """
    Limit request body size to prevent memory exhaustion attacks.
    """
    MAX_REQUEST_SIZE = 16 * 1024  # 16KB - generous for text requests

    # Check Content-Length header
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return JSONResponse(
            status_code=413,
            content={"error": "Request too large. Maximum size is 16KB."}
        )

    # For requests without Content-Length, we'll let FastAPI's natural limits handle it
    response = await call_next(request)
    return response

# --- Database Connection Management ---
DB_PATH = os.path.join(os.path.dirname(__file__), 'monitoring.db')

def get_database():
    """
    FastAPI dependency: open a fresh SQLite connection per request and close it afterwards.
    This avoids cross-thread reuse and reduces locking issues.
    """
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,   # allow usage in async/threaded contexts
        timeout=30
    )
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        yield conn
    finally:
        conn.close()

# --- Application Startup Event ---
@app.on_event("startup")
async def startup_event():
    """
    This function is called when the FastAPI application starts.
    """
    print("🚀 Starting MacDonald History Bot API...")

    try:
        # Initialize database with a short-lived connection
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
            setup_database(conn)
            setup_share_database(conn)
        print("✅ Database initialization completed")

        # Validate external dependencies
        print("🔍 Validating external dependencies...")

        # Test ChromaDB collection access
        try:
            collection.count()  # Simple test
            print("✅ ChromaDB collection accessible")
        except Exception as e:
            print(f"❌ ChromaDB validation failed: {e}")
            raise

        # Test embedding model
        try:
            embedder.encode("test")  # Simple test
            print("✅ Embedding model loaded and functional")
        except Exception as e:
            print(f"❌ Embedding model validation failed: {e}")
            raise

        # Test OpenRouter connectivity (optional - don't want to waste API calls)
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if len(openrouter_key) < 20:  # Basic sanity check
            raise ValueError("OPENROUTER_API_KEY appears to be invalid (too short)")
        print("✅ OpenRouter API key format validation passed")

        print("🎉 Application startup completed successfully")

    except Exception as e:
        print(f"💥 Startup failed: {e}")
        print("❌ Application will not start due to validation errors")
        raise  # This will prevent the app from starting

# Remove the shutdown event entirely - no longer needed


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

---

**Language note:** Do not use outdated or offensive phrases such as “the Indian problem” or other language that would be considered harmful today. Speak with respect and care when referring to Indigenous peoples and sensitive historical topics.
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
embedder = SentenceTransformer("paraphrase-MiniLM-L3-v2")

# Load ChromaDB collection
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("macdonald_speeches")


# Production security middleware (only in production)
if ENVIRONMENT == "production":
    # Enforce HTTPS in production
    app.add_middleware(HTTPSRedirectMiddleware)

    # Validate trusted hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS
    )

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Still configurable via environment variable
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[  # More specific headers instead of "*"
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "User-Agent",
        "DNT",
        "Cache-Control",
        "X-Mx-ReqToken",
        "Keep-Alive",
        "X-Requested-With",
        "If-Modified-Since"
    ],
    expose_headers=["Content-Length", "Content-Type"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Add security headers
    if ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Always add these headers
    response.headers["X-API-Version"] = "1.0.0"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response

class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question about Canadian history"
    )

    @validator('question')
    def validate_question(cls, v):
        # Remove extra whitespace and validate
        v = v.strip()
        if not v:
            raise ValueError('Question cannot be empty')

        # Check for suspicious patterns (basic protection)
        if any(suspicious in v.lower() for suspicious in ['<script', 'javascript:', 'data:', 'vbscript:']):
            raise ValueError('Question contains invalid content')

        return v

class ShareRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    answer: str = Field(..., min_length=1, max_length=10000, description="AI response")
    sources: list = Field(..., max_items=10, description="Source references")

    @validator('question', 'answer')
    def validate_text_fields(cls, v):
        if not v.strip():
            raise ValueError('Text fields cannot be empty')
        return v.strip()

    @validator('sources')
    def validate_sources(cls, v):
        if len(v) > 10:
            raise ValueError('Too many source references')
        return v

@app.get("/")
def read_root():
    return {"message": "Welcome to the John A. Macdonald chatbot API."}

@app.post("/api/ask") # Prefixed with /api
@limiter.limit("10/minute")  # Apply a rate limit of 10 requests per minute to this endpoint
def ask_macdonald(
    question_request: QuestionRequest,
    request: Request,
    db: sqlite3.Connection = Depends(get_database)  # Add this dependency
):

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
            print(f"Detailed response data: {response_data}")  # Log for debugging
            log_request(
                conn=db,
                user_ip=user_ip, question=question_request.question, is_successful=False,
                latency_ms=latency, error_message=f"Unexpected response format: {response_data}"
            )
            return {"error": "I'm experiencing technical difficulties. Please try again in a moment."}  # Generic message

        # Extract the answer
        answer = response_data["choices"][0]["message"]["content"]

        # Log the successful request
        log_request(
            conn=db,
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
            conn=db,
            user_ip=user_ip, question=question_request.question, is_successful=False,
            latency_ms=latency, error_message=error_msg
        )
        return {"error": error_msg}
    except KeyError as e:
        print(f"KeyError: {e}")
        print(f"Response data: {response_data}")  # Keep detailed logging
        log_request(
            conn=db,
            user_ip=user_ip, question=question_request.question, is_successful=False,
            latency_ms=latency, error_message=f"KeyError: {e}, Response: {response_data}"
        )
        return {"error": "I'm experiencing technical difficulties. Please try again in a moment."}
    except Exception as e:
        print(f"Unexpected error: {e}")  # Keep detailed logging
        log_request(
            conn=db,
            user_ip=user_ip, question=question_request.question, is_successful=False,
            latency_ms=latency, error_message=f"Unexpected error: {str(e)}"
        )
        return {"error": "I'm unable to respond at the moment. Please try again shortly."}

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
@limiter.limit("5/minute")  # Allow 5 share creations per minute per IP
async def share_conversation(
    share_request: ShareRequest,
    request: Request,  # Add this for rate limiting
    db: sqlite3.Connection = Depends(get_database)
):
    """
    Creates a permanent, shareable link for a given conversation.
    """
    share_id = create_share_link(
        conn=db,
        question=share_request.question,
        answer=share_request.answer,
        sources=share_request.sources
    )
    if share_id:
        return {"share_id": share_id}
    else:
        return JSONResponse(status_code=500, content={"error": "Could not create share link."})

@app.get("/api/share/{share_id}")
@limiter.limit("20/minute")  # Allow 20 share retrievals per minute per IP (more lenient since it's read-only)
async def get_conversation(
    share_id: str,
    request: Request,  # Add this for rate limiting
    db: sqlite3.Connection = Depends(get_database)
):
    """
    Retrieves a shared conversation by its unique ID.
    """
    shared_data = get_shared_link(conn=db, share_id=share_id)
    if shared_data:
        return shared_data
    else:
        return JSONResponse(status_code=404, content={"error": "Shared conversation not found."})


# --- Frontend Serving ---

# Define the path to the built frontend files



