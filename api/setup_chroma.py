"""
Setup script to rebuild the ChromaDB vector store from historical documents.
Run this after cloning the repository to set up the vector database.
"""
import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

def setup_chroma_db():
    print("Setting up ChromaDB vector store...")

    # Initialize the embedding model
    print("Loading embedding model...")
    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        print(f"[ERROR] Failed to load embedding model: {e}")
        sys.exit(1)

    # Create ChromaDB client
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_store")
        collection = chroma_client.get_or_create_collection("macdonald_speeches")
    except Exception as e:
        print(f"[ERROR] Failed to setup ChromaDB: {e}")
        sys.exit(1)

    # Process all JSON files in the output directory
    output_dir = Path("output")

    if not output_dir.exists():
        print(f"[ERROR] Output directory '{output_dir}' does not exist.")
        print("Please run the extraction scripts first to generate JSON files.")
        sys.exit(1)

    documents = []
    metadatas = []
    ids = []

    json_files = list(output_dir.glob("*.json"))
    if not json_files:
        print(f"[ERROR] No JSON files found in '{output_dir}' directory.")
        sys.exit(1)

    doc_id = 0
    for json_file in json_files:
        print(f"Processing {json_file.name}...")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read {json_file.name}: {e}")
            continue

        if not isinstance(data, list):
            print(f"[WARNING]  Skipping {json_file.name}: Expected list format")
            continue

        for entry in data:
            try:
                # Fix: Use 'content' instead of 'text' to match extraction script output
                content = entry.get('content', '')
                if not content:
                    print(f"[WARNING]  Skipping empty content in {json_file.name}")
                    continue

                documents.append(content)

                # Fix: Preserve all available metadata instead of just basic fields
                metadata = {
                    'speaker': entry.get('speaker', 'Unknown'),
                    'source': entry.get('source', json_file.name),
                    'page': entry.get('page', 0),
                    'year': entry.get('year', 0),
                    'chunk_index': entry.get('chunk_index', 0)
                }

                # Add optional metadata fields if they exist
                if 'parliament' in entry and entry['parliament'] is not None:
                    metadata['parliament'] = entry['parliament']
                if 'session' in entry and entry['session'] is not None:
                    metadata['session'] = entry['session']
                if 'volume' in entry and entry['volume'] is not None:
                    metadata['volume'] = entry['volume']

                metadatas.append(metadata)

                # Fix: Use unique doc_id to prevent duplicates
                chunk_id = f"parl_{entry.get('parliament', 'unknown')}_sess_{entry.get('session', 'unknown')}_{json_file.stem}_{doc_id}"
                ids.append(chunk_id)

                doc_id += 1

            except Exception as e:
                print(f"[WARNING]  Skipping corrupted entry in {json_file.name}: {e}")
                continue

    if not documents:
        print("[ERROR] No valid documents found to process.")
        sys.exit(1)

    print(f"Adding {len(documents)} documents to ChromaDB...")

    # Add documents in batches to avoid memory issues
    batch_size = 100
    total_batches = (len(documents) - 1) // batch_size + 1

    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        try:
            # Generate embeddings
            embeddings = embedder.encode(batch_docs).tolist()

            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=embeddings,
                ids=batch_ids
            )

            print(f"[SUCCESS] Processed batch {i//batch_size + 1}/{total_batches}")

        except Exception as e:
            print(f"[ERROR] Failed to process batch {i//batch_size + 1}: {e}")
            continue

    print("[SUCCESS] ChromaDB setup complete!")
    print(f"Total documents indexed: {len(documents)}")

    # Show collection stats
    try:
        collection_count = collection.count()
        print(f"Collection now contains: {collection_count} documents")
    except Exception as e:
        print(f"[WARNING]  Could not verify collection count: {e}")

if __name__ == "__main__":
    setup_chroma_db()