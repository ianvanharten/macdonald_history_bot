import chromadb
import ollama
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

def format_prompt(chunks, question):
    """
    Formats historical excerpts and the user's question into a prompt for Gemma.
    """
    context = "\n\n".join([
        f"[Excerpt from {meta['source']} - page {meta['page']}, {meta['year']}]\n{doc}"
        for doc, meta in chunks
    ])

    return f"""
You are Sir John A. Macdonald, Canada's first Prime Minister. Speak in the first person, as if you are personally answering the user's question.

Your task is to respond to the user's question in a way that is:
- Faithful to your historical views, tone, and character
- Understandable and educational for a modern audience
- Grounded only in the provided historical excerpts
- Supported with quotes directly from those excerpts, when appropriate
- Enriched with brief historical context when referencing people, events, or ideas that modern readers may not be familiar with

Avoid speculation or modern references. Do not include information not found in the excerpts below.
You must always speak in the **first person**, referring to yourself as "I", and never in the third person (do not say “Sir John A. Macdonald” or “he”). Maintain the tone of a thoughtful 19th-century statesman.
Use a formal tone consistent with 19th-century speech, but ensure your answer is clear and informative for present-day readers.
At the end of your answer, suggest 1 or 2 thoughtful follow-up questions the user might ask next, based on the topic you discussed. Format these clearly, such as in a bulleted list.

Historical excerpts:
{context}

User's question:
{question}
"""


# Load embedding model (same one used for indexing)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load ChromaDB collection - Updated to new API
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("macdonald_speeches")

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the John A. Macdonald chatbot API."}

@app.post("/ask")
def ask_macdonald(request: QuestionRequest):
    question_embedding = embedder.encode(request.question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    chunks = list(zip(results["documents"][0], results["metadatas"][0]))
    prompt = format_prompt(chunks, request.question)

    response = ollama.chat(
        model="llama3.2:1b",  # or "tinyllama" if you want to swap
        messages=[
            {"role": "system", "content": "You are Sir John A. Macdonald, speaking in formal 19th-century Canadian English."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response["message"]["content"]

    # Try to split off the follow-up suggestions
    answer_parts = answer.strip().split("\n\n")
    main_response = answer_parts[0].strip()
    follow_ups = []

    for part in answer_parts[1:]:
        if "follow-up" in part.lower() or "-" in part or "?" in part:
            follow_ups = [
                line.strip("–-•* ").strip()
                for line in part.strip().splitlines()
                if "?" in line
            ]
            break


    return {
    "question": request.question,
    "answer": main_response,
    "sources": [
      {
          "quote": doc,
          "source": meta["source"],
          "page": meta["page"],
          "year": meta["year"]
      }
      for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ],
    "follow_ups": follow_ups
}



