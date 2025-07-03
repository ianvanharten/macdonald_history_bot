import os
import fitz  # PyMuPDF
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === CONFIGURATION ===
PDF_FILE = "MLIConfederationSeries_MacdonaldPaperF_Web.pdf"
SOURCE_NAME = "macdonald_mli"
CHUNK_SIZE = 500  # words
COLLECTION_NAME = "macdonald_speeches"
PERSIST_DIR = "./chroma_store"

# === SETUP ===
print("🔧 Loading embedding model and ChromaDB...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=PERSIST_DIR)

collection = client.get_or_create_collection(name=COLLECTION_NAME)

# === HELPERS ===

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def extract_pdf_text(filepath):
    doc = fitz.open(filepath)
    all_pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        all_pages.append((i + 1, text))  # page numbers start at 1
    return all_pages

# === MAIN LOGIC ===

print(f"📖 Reading {PDF_FILE}...")
pages = extract_pdf_text(PDF_FILE)
total_chunks = 0

for page_number, text in tqdm(pages, desc="📄 Processing pages"):
    chunks = chunk_text(text, CHUNK_SIZE)
    for chunk_index, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        chunk_id = str(uuid.uuid4())

        metadata = {
            "source": SOURCE_NAME,
            "page": page_number,
            "chunk_index": chunk_index,
            "year": 1921,
            "speaker": "Narrator"
        }

        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[metadata]
        )
        total_chunks += 1

print(f"\n✅ Ingestion complete: {total_chunks} chunks added from {PDF_FILE} into ChromaDB.")
