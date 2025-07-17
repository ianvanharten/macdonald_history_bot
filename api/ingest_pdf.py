import os
import fitz  # PyMuPDF
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import requests
import io
from urllib.parse import urlparse

# === CONFIGURATION ===
PDF_URLS = [
    "https://primarydocuments.ca/wp-content/uploads/2019/03/PopeMacdonaldCorrespondence.pdf",
    "https://macdonaldlaurier.ca/files/pdf/MLIConfederationSeries_MacdonaldPaperF_Web.pdf"
]

SOURCE_NAMES = {
    "primarydocuments.ca": "macdonald_correspondence",
    "macdonaldlaurier.ca": "macdonald_mli"
}

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

def get_source_name(url):
    """Extract source name from URL"""
    domain = urlparse(url).netloc
    return SOURCE_NAMES.get(domain, domain.replace("www.", ""))

def extract_pdf_from_url(url):
    """Download PDF from URL and extract text"""
    print(f"📄 Downloading PDF from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Open PDF from memory (no need to save to disk)
        pdf_data = io.BytesIO(response.content)
        doc = fitz.open(stream=pdf_data, filetype="pdf")

        all_pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            all_pages.append((i + 1, text))  # page numbers start at 1

        doc.close()
        return all_pages

    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading PDF from {url}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error processing PDF from {url}: {e}")
        return []

def process_pdf_url(url):
    """Process a single PDF URL"""
    source_name = get_source_name(url)
    print(f"📖 Processing {source_name} from {url}...")

    pages = extract_pdf_from_url(url)
    if not pages:
        return 0

    total_chunks = 0

    for page_number, text in tqdm(pages, desc=f"📄 Processing {source_name} pages"):
        chunks = chunk_text(text, CHUNK_SIZE)
        for chunk_index, chunk in enumerate(chunks):
            if chunk.strip():  # Only process non-empty chunks
                embedding = embedder.encode(chunk).tolist()
                chunk_id = str(uuid.uuid4())

                metadata = {
                    "source": source_name,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "year": 1921,  # Customize per source if needed
                    "speaker": "Narrator",
                    "url": url
                }

                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[metadata]
                )
                total_chunks += 1

    return total_chunks

# === MAIN LOGIC ===

print("🚀 Starting PDF ingestion from URLs...")
grand_total = 0

for url in PDF_URLS:
    chunks_added = process_pdf_url(url)
    grand_total += chunks_added
    print(f"✅ Added {chunks_added} chunks from {get_source_name(url)}")

print(f"\n🎉 Ingestion complete! Total chunks added: {grand_total}")
