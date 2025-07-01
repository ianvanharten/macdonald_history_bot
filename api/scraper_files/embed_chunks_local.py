import os
import json
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Load local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Small, fast, good quality

# Setup ChromaDB client with new API
client = chromadb.PersistentClient(path="./chroma_store")

# Create a collection (or load it)
collection = client.get_or_create_collection(name="macdonald_speeches")

# Load chunks from JSON files
def load_chunks(folder_path):
    all_chunks = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                all_chunks.extend(data)
    return all_chunks

# Generate embeddings locally
def get_embedding(text):
    return model.encode(text).tolist()

# Main loop to embed and store
def embed_and_store(chunks):
    for i, chunk in enumerate(tqdm(chunks)):
        try:
            # More descriptive chunk ID that includes parliament and session
            chunk_id = f"parl_{chunk.get('parliament', 'unknown')}_sess_{chunk.get('session', 'unknown')}_{chunk['source']}_{chunk['page']}_{chunk['chunk_index']}"
            embedding = get_embedding(chunk["content"])

            # Build metadata - include all available fields
            metadata = {
                "speaker": chunk["speaker"],
                "parliament": chunk.get("parliament"),
                "session": chunk.get("session"),
                "year": chunk["year"],
                "page": chunk["page"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"]
            }

            # Only add volume if it exists
            if "volume" in chunk and chunk["volume"] is not None:
                metadata["volume"] = chunk["volume"]

            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk["content"]],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"❌ Failed to embed chunk {i}: {e}")
            print(f"   Chunk data: {chunk}")  # Debug info

if __name__ == "__main__":
    chunk_folder = "./output"  # Folder containing your JSON files
    chunks = load_chunks(chunk_folder)
    embed_and_store(chunks)
    print("✅ Embedding complete! Stored in ./chroma_store")
