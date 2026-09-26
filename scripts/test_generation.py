import sys
sys.path.insert(0, ".")

from app.generation.chain import answer

result = answer(sys.argv[1])

print("RÉPONSE:\n", result["answer"])
print("\nSOURCES:")
for s in result["sources"]:
    print(f"- {s['source']} (pages {s['pages']}, score={s['score']:.4f})")