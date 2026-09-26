import sys
sys.path.insert(0, ".")

from app.ingestion.loader import load_and_chunk

chunks = load_and_chunk(sys.argv[1])
lengths = [len(c.page_content) for c in chunks]

print(f"{len(chunks)} chunks | avg {sum(lengths) // max(len(lengths), 1)} chars | max {max(lengths)}")
for c in chunks[:3]:
    print("\nMETADATA:", c.metadata)
    print("TEXT:", c.page_content[:300])
