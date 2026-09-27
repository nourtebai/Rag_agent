import sys
sys.path.insert(0, ".")

import psycopg

from app.config import settings

url = settings.database_url.replace("+psycopg", "")
with psycopg.connect(url) as conn:
    rows = conn.execute(
        "SELECT cmetadata->>'source' AS source, count(*) "
        "FROM langchain_pg_embedding "
        "GROUP BY source "
        "ORDER BY source"
    ).fetchall()

    total = 0
    for source, count in rows:
        print(f"{source}: {count} chunks")
        total += count

    print(f"\nTOTAL: {total}")