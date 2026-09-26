import sys
sys.path.insert(0, ".")

from app.ingestion.loader import load_and_chunk
from app.retrieval.store import get_vector_store

file_path = sys.argv[1]

print(f"Chunking {file_path}...")
chunks = load_and_chunk(file_path)
print(f"{len(chunks)} chunks produced")

print("Embedding and storing...")
store = get_vector_store()
ids = store.add_documents(chunks)

print(f"{len(ids)} chunks stored in the '{store.collection_name}' collection")