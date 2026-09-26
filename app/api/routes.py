import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.agent.graph import run_agent
from app.ingestion.loader import load_and_chunk
from app.retrieval.store import get_vector_store
from app.api.schemas import AskRequest, AskResponse, IngestResponse

router = APIRouter()
UPLOAD_DIR = Path("data")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/ingest", response_model=IngestResponse)
def ingest(file: UploadFile):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    dest = UPLOAD_DIR / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks = load_and_chunk(str(dest))
    if not chunks:
        raise HTTPException(422, "No content could be extracted from this file")

    store = get_vector_store()
    ids = store.add_documents(chunks)

    return IngestResponse(filename=file.filename, chunks_stored=len(ids))


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    result = await run_agent(request.question)
    return AskResponse(answer=result)