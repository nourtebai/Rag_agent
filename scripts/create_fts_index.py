import sys
sys.path.insert(0, ".")

import psycopg

from app.config import settings

url = settings.database_url.replace("+psycopg", "")
with psycopg.connect(url, autocommit=True) as conn:
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_fts ON langchain_pg_embedding "
        "USING GIN (to_tsvector('french', document));"
    )
    print("Index plein texte créé")