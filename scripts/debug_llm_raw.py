import sys
sys.path.insert(0, ".")

from app.agent.graph import get_llm

question = sys.argv[1]
prompt = """Classe cette question dans une seule catégorie : rag, web, ou direct.
'rag' = contenu de documents internes déjà indexés.
'web' = information actuelle ou externe (taux de change, météo, actualité).
'direct' = question générale ou conversationnelle.

Réponds uniquement par un mot : rag, web, ou direct."""

llm = get_llm()
response = llm.invoke([("system", prompt), ("human", question)])
print("Réponse brute du LLM :", repr(response.content))