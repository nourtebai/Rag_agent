import sys
sys.path.insert(0, ".")

import psycopg
from langchain_ollama import ChatOllama, OllamaEmbeddings
from app.config import settings


def check(name, fn):
    try:
        print(f"OK  {name}:", fn())
    except Exception as e:
        print(f"ERR {name}:", e)


def check_db():
    url = settings.database_url.replace("+psycopg", "")
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        row = conn.execute(
            "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
        ).fetchone()
        return f"Postgres + pgvector {row[0]}"


def check_embeddings():
    emb = OllamaEmbeddings(model=settings.embedding_model, base_url=settings.ollama_base_url)
    return f"dimension = {len(emb.embed_query('test'))}"


def check_llm():
    llm = ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url)
    return llm.invoke("Dis bonjour en une phrase").content


check("Database", check_db)
check("Embeddings", check_embeddings)
check("LLM", check_llm)
