import psycopg

from app.config import settings
from app.retrieval.store import get_embeddings


def _get_collection_id(conn) -> str:
    row = conn.execute(
        "SELECT uuid FROM langchain_pg_collection WHERE name = %s",
        (settings.collection_name,),
    ).fetchone()
    if not row:
        raise ValueError(f"Collection '{settings.collection_name}' introuvable")
    return row[0]


def hybrid_search(query: str, k: int = 20) -> list[dict]:
    """Recherche hybride : fusionne un classement vectoriel et un classement
    plein texte (BM25-like) via Reciprocal Rank Fusion."""
    embeddings = get_embeddings()
    query_vector = embeddings.embed_query(query)
    vector_literal = "[" + ",".join(str(x) for x in query_vector) + "]"

    url = settings.database_url.replace("+psycopg", "")
    with psycopg.connect(url) as conn:
        collection_id = _get_collection_id(conn)

        rows = conn.execute(
            """
            WITH vector_search AS (
                SELECT id, document, cmetadata,
                       RANK() OVER (ORDER BY embedding <=> %(qvec)s::vector) AS rank
                FROM langchain_pg_embedding
                WHERE collection_id = %(cid)s
                ORDER BY embedding <=> %(qvec)s::vector
                LIMIT %(k)s
            ),
            fts_search AS (
                SELECT id, document, cmetadata,
                       RANK() OVER (
                           ORDER BY ts_rank_cd(to_tsvector('french', document), plainto_tsquery('french', %(qtext)s)) DESC
                       ) AS rank
                FROM langchain_pg_embedding
                WHERE collection_id = %(cid)s
                  AND to_tsvector('french', document) @@ plainto_tsquery('french', %(qtext)s)
                LIMIT %(k)s
            )
            SELECT
                COALESCE(v.id, f.id) AS id,
                COALESCE(v.document, f.document) AS document,
                COALESCE(v.cmetadata, f.cmetadata) AS cmetadata,
                COALESCE(1.0 / (60 + v.rank), 0) + COALESCE(1.0 / (60 + f.rank), 0) AS rrf_score
            FROM vector_search v
            FULL OUTER JOIN fts_search f ON v.id = f.id
            ORDER BY rrf_score DESC
            LIMIT %(k)s
            """,
            {"qvec": vector_literal, "qtext": query, "cid": collection_id, "k": k},
        ).fetchall()

    results = []
    for _id, document, cmetadata, rrf_score in rows:
        results.append({
            "content": document,
            "source": cmetadata.get("source"),
            "pages": cmetadata.get("pages"),
            "headings": cmetadata.get("headings"),
            "score": rrf_score,
        })
    return results