# RAG Agent — Agentic RAG avec Supervisor et MCP

Assistant documentaire qui répond à des questions à partir de documents PDF, avec routage intelligent, citations de sources, et outils exposés via le protocole MCP.

## Architecture

PDF → Docling (extraction) → chunking → embeddings (bge-m3) → Postgres/pgvector
↓
FastAPI (/ingest, /ask) → Supervisor LangGraph (route "rag" ou "direct")
↓
Client MCP → Serveur MCP → search_knowledge_base
↓
LangSmith (traçabilité complète)


## Stack

- **Extraction** : Docling
- **Orchestration** : LangChain + LangGraph
- **LLM & embeddings** : Ollama (qwen3:8b, bge-m3), local
- **Base de données** : PostgreSQL + pgvector
- **API** : FastAPI
- **Outils** : MCP (Model Context Protocol)
- **Observabilité** : LangSmith

## Prérequis

- Python 3.12
- Docker Desktop
- Ollama (`ollama pull qwen3:8b`, `ollama pull bge-m3`)

## Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d
```

Copier `.env.example` en `.env` et renseigner les variables si besoin.

## Utilisation

**1. Ingérer des documents** (placer les PDF dans `data/`) :
```powershell
python scripts\ingest_all.py
```

**2. Lancer l'API :**
```powershell
uvicorn app.main:app --reload
```

**3. Tester :** ouvrir http://127.0.0.1:8000/docs, ou en ligne de commande :
```powershell
python scripts\test_agent.py "votre question"
```

## Fonctionnement du routage

Le Supervisor analyse chaque question et choisit :
- **`rag`** : recherche dans les documents indexés via l'outil MCP, réponse sourcée
- **`direct`** : réponse directe du LLM, sans recherche (questions conversationnelles)

## Structure du projet

app/
├── ingestion/ # Docling, chunking (loader.py, batch.py)
├── retrieval/ # stockage pgvector, recherche par similarité
├── generation/ # chaîne RAG avec citations
├── agent/ # graphe LangGraph Supervisor
├── mcp_tools/ # serveur MCP
├── api/ # routes FastAPI
scripts/ # scripts de test pour chaque étape