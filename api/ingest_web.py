import requests
from bs4 import BeautifulSoup
import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from urllib.parse import urlparse

# === CONFIGURATION ===
WEB_URLS = [
    "https://www.thecanadianencyclopedia.ca/en/article/sir-john-alexander-macdonald",
    "https://www.johnamacdonald.org/",
    "https://www.johnamacdonald.org/p/macdonald-x.html",
    "https://www.johnamacdonald.org/p/xxii-end.html",  # Fixed this URL
    "https://en.wikipedia.org/wiki/John_A._Macdonald"
]

SOURCE_NAMES = {
    "thecanadianencyclopedia.ca": "canadian_encyclopedia",
    "biographi.ca": "dictionary_canadian_biography",
    "johnamacdonald.org": "anecdotal_life_macdonald",
    "en.wikipedia.org": "macdonald_wikipedia"
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

def extract_visible_text(url):
    """Extract text from web page with site-specific handling"""
    print(f"🌐 Fetching {url}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"📊 Response length: {len(response.text)} characters")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Site-specific handling
        if 'wikipedia.org' in url:
            # Wikipedia-specific extraction (as before)
            for tag in soup(['script', 'style', 'sup', 'table']):
                tag.decompose()
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                text = content_div.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)

        elif 'thecanadianencyclopedia.ca' in url:
            # Canadian Encyclopedia - focus on article content
            for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            article = soup.find('article') or soup.find('div', class_='article-content')
            if article:
                text = article.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)

        elif 'johnamacdonald.org' in url:
            # John A MacDonald site - minimal filtering
            for tag in soup(['script', 'style']):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)

        else:
            # Default handling for other sites
            for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)

        print(f"📊 Extracted text length: {len(text)} characters")
        return text

    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
        return ""

def process_web_url(url):
    """Process a single web URL"""
    source_name = get_source_name(url)
    print(f"📄 Processing {source_name} from {url}...")

    raw_text = extract_visible_text(url)
    if not raw_text:
        return 0

    chunks = chunk_text(raw_text, CHUNK_SIZE)
    total_chunks = 0

    for chunk_index, chunk in enumerate(tqdm(chunks, desc=f"🧠 Processing {source_name} chunks")):
        if chunk.strip():  # Only process non-empty chunks
            embedding = embedder.encode(chunk).tolist()
            chunk_id = str(uuid.uuid4())

            metadata = {
                "source": source_name,
                "chunk_index": chunk_index,
                "year": 2024,  # You can customize this per source if needed
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

print("🚀 Starting web content ingestion from URLs...")
grand_total = 0

for url in WEB_URLS:
    chunks_added = process_web_url(url)
    grand_total += chunks_added
    print(f"✅ Added {chunks_added} chunks from {get_source_name(url)}")

print(f"\n🎉 Ingestion complete! Total chunks added: {grand_total}")
