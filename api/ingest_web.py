import requests
from bs4 import BeautifulSoup
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === CONFIGURATION ===
URL = "https://en.wikipedia.org/wiki/John_A._Macdonald"  # Example
SOURCE_NAME = "macdonald_wikipedia"
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

def extract_visible_text(url):
    print(f"🌐 Fetching {url}...")
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    # Remove scripts, styles, and nav elements
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        tag.decompose()

    text = soup.get_text(separator=' ', strip=True)
    return text

# === MAIN LOGIC ===

print("📄 Extracting and processing web content...")
raw_text = extract_visible_text(URL)
chunks = chunk_text(raw_text, CHUNK_SIZE)

for i, chunk in enumerate(tqdm(chunks, desc="🧠 Embedding & adding chunks")):
    embedding = embedder.encode(chunk).tolist()
    chunk_id = str(uuid.uuid4())

    metadata = {
        "source": SOURCE_NAME,
        "chunk_index": i,
        "year": 2024,  # or estimate
        "speaker": "Narrator"
    }

    collection.add(
        ids=[chunk_id],
        embeddings=[embedding],
        documents=[chunk],
        metadatas=[metadata]
    )

print(f"\n✅ Ingestion complete: {len(chunks)} chunks added from {URL} into ChromaDB.")
