import sys
sys.path.insert(0, ".")

from app.retrieval.retriever import search

query = sys.argv[1]
results = search(query)

for i, r in enumerate(results, 1):
    print(f"\n#{i} | score={r['score']:.4f} | source={r['source']} | pages={r['pages']}")
    print(f"headings: {r['headings']}")
    print(r['content'][:300])