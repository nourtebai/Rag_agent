# RAG Agent — Agentic RAG avec Supervisor, fallback web et MCP

Assistant documentaire qui répond à des questions à partir de documents PDF, avec routage intelligent, fallback automatique vers le web, citations de sources, et outils exposés via le protocole MCP.

## Architecture

PDF → Docling (extraction) → chunking → embeddings (bge-m3) → Postgres/pgvector
↓
FastAPI (/ingest, /ask) → Supervisor LangGraph (route "search" ou "direct")
↓
"direct" → réponse LLM immédiate (pas d'outil)
"search" → RAG (MCP, search_knowledge_base) en priorité
├─→ réponse trouvée → fin
└─→ "je ne trouve pas..." → fallback automatique
→ web_search (MCP) → réponse sourcée
↓
LangSmith (traçabilité complète de chaque étape)


Le Supervisor ne décide que si une recherche est nécessaire, jamais où chercher : c'est le RAG lui-même qui juge s'il a de quoi répondre, et déclenche le fallback web si besoin. Cette approche évite de maintenir une liste de mots-clés pour distinguer "question sur mes documents" de "question externe" — elle s'adapte automatiquement à n'importe quel nouveau document ajouté.

## Stack

- **Extraction** : Docling
- **Orchestration** : LangChain + LangGraph
- **LLM & embeddings** : Ollama (qwen3:8b, bge-m3), local
- **Base de données** : PostgreSQL + pgvector
- **API** : FastAPI
- **Outils** : MCP (Model Context Protocol) — `search_knowledge_base` (documents indexés) et `web_search` (recherche web, via ddgs, sans clé API)
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

Copier `.env.example` en `.env` et renseigner les variables si besoin (base de données, LangSmith).

## Utilisation

**1. Ingérer des documents** (placer un ou plusieurs PDF dans `data/`) :
```powershell
python scripts\ingest_all.py
```
Réingérer un fichier déjà présent remplace automatiquement ses anciens chunks (pas de doublons).

**2. Lancer l'API :**
```powershell
uvicorn app.main:app --reload
```

**3. Tester :**
- Interface : http://127.0.0.1:8000/docs
- Ligne de commande :
```powershell
  python scripts\test_agent.py "votre question"
```
- Diagnostic du routage et du chemin emprunté (rag / web / direct) :
```powershell
  python scripts\debug_route.py "votre question"
  python scripts\debug_path.py "votre question"
```

## Structure du projet

app/
├── ingestion/ # Docling, chunking (loader.py, batch.py)
├── retrieval/ # stockage pgvector, recherche par similarité, dédoublonnage
├── generation/ # chaîne RAG simple avec citations (étape de base, avant l'agent)
├── agent/ # graphe LangGraph Supervisor + fallback RAG→web
├── mcp_tools/ # serveur MCP (search_knowledge_base, web_search)
├── api/ # routes FastAPI (/ingest, /ask, branché sur l'agent)
scripts/ # scripts de test et de diagnostic pour chaque étape


## Observabilité

Les traces LangSmith montrent, pour chaque question, le nœud du Supervisor traversé, les appels d'outils (RAG et/ou web), et la réponse finale — utile pour diagnostiquer un mauvais routage ou un retrieval peu pertinent sans deviner à l'aveugle.