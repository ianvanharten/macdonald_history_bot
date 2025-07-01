"""
Setup script to rebuild the ChromaDB vector store from historical documents.
Run this after cloning the repository to set up the vector database.
"""
import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

def setup_chroma_db():
    print("Setting up ChromaDB vector store...")

    # Initialize the embedding model
    print("Loading embedding model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # Create ChromaDB client
    chroma_client = chromadb.PersistentClient(path="./chroma_store")
    collection = chroma_client.get_or_create_collection("macdonald_speeches")

    # Process all JSON files in the output directory
    output_dir = Path("output")
    documents = []
    metadatas = []
    ids = []

    doc_id = 0
    for json_file in output_dir.glob("*.json"):
        print(f"Processing {json_file.name}...")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data:
            documents.append(entry['text'])
            metadatas.append({
                'source': entry['source'],
                'page': entry['page'],
                'year': entry['year']
            })
            ids.append(str(doc_id))
            doc_id += 1

    print(f"Adding {len(documents)} documents to ChromaDB...")

    # Add documents in batches to avoid memory issues
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        # Generate embeddings
        embeddings = embedder.encode(batch_docs).tolist()

        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            embeddings=embeddings,
            ids=batch_ids
        )

        print(f"Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

    print("ChromaDB setup complete!")
    print(f"Total documents indexed: {len(documents)}")

if __name__ == "__main__":
    setup_chroma_db()