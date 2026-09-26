import psycopg

from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

from app.config import settings


def get_embeddings():
    return OllamaEmbeddings(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
    )


def get_vector_store():
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=settings.collection_name,
        connection=settings.database_url,
        use_jsonb=True,
    )


def delete_by_source(source: str) -> int:
    """Supprime tous les chunks existants d'un fichier donné, retourne le nombre supprimé."""
    url = settings.database_url.replace("+psycopg", "")
    with psycopg.connect(url, autocommit=True) as conn:
        result = conn.execute(
            """
            DELETE FROM langchain_pg_embedding e
            USING langchain_pg_collection c
            WHERE e.collection_id = c.uuid
              AND c.name = %s
              AND e.cmetadata->>'source' = %s
            """,
            (settings.collection_name, source),
        )
        return result.rowcount