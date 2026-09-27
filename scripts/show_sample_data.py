import sys
sys.path.insert(0, ".")

import psycopg

from app.config import settings

source_filter = sys.argv[1] if len(sys.argv) > 1 else None

url = settings.database_url.replace("+psycopg", "")
with psycopg.connect(url) as conn:
    if source_filter:
        rows = conn.execute(
            "SELECT document, cmetadata, embedding FROM langchain_pg_embedding "
            "WHERE cmetadata->>'source' ILIKE %s "
            "ORDER BY (cmetadata->'pages'->>0)::int",
            (f"%{source_filter}%",),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT document, cmetadata, embedding FROM langchain_pg_embedding LIMIT 5"
        ).fetchall()

    if not rows:
        print(f"Aucun chunk trouvé pour '{source_filter}'")
    else:
        for i, (document, cmetadata, embedding) in enumerate(rows, 1):
            vector = list(embedding)
            print(f"\n--- Chunk {i}/{len(rows)} ---")
            print("METADATA:", cmetadata)
            print("TEXTE:", document[:200])
            print(f"EMBEDDING (dimension {len(vector)}):", vector[:6], "...")

    label = f"pour '{source_filter}'" if source_filter else "affichés (limite 5)"
    print(f"\nTOTAL CHUNKS {label}: {len(rows)}")