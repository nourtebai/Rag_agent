import sys
sys.path.insert(0, ".")

from app.retrieval.hybrid import hybrid_search

results = hybrid_search(sys.argv[1], k=10)
for i, r in enumerate(results, 1):
    print(f"\n#{i} | rrf_score={r['score']:.5f} | source={r['source']} | pages={r['pages']}")
    print(r["content"][:200])