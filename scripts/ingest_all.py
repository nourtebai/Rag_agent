import sys
sys.path.insert(0, ".")

from pathlib import Path

from app.ingestion.batch import load_all
from app.ingestion.loader import load_and_chunk
from app.retrieval.store import get_vector_store, delete_by_source

DATA_DIR = "data"

print(f"Scan de {DATA_DIR}/...")
store = get_vector_store()

pdf_files = sorted(Path(DATA_DIR).glob("*.pdf"))
if not pdf_files:
    print("Aucun PDF trouvé.")
    sys.exit(0)

total_stored = 0
for pdf in pdf_files:
    deleted = delete_by_source(pdf.name)
    if deleted:
        print(f"{pdf.name}: {deleted} anciens chunks supprimés")

    chunks = load_and_chunk(str(pdf))
    if not chunks:
        print(f"{pdf.name}: aucun contenu extrait, ignoré")
        continue

    ids = store.add_documents(chunks)
    total_stored += len(ids)
    print(f"{pdf.name}: {len(ids)} chunks stockés")

print(f"\nTerminé : {total_stored} chunks au total pour {len(pdf_files)} fichier(s).")