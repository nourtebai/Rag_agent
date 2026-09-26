from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str



class SourceItem(BaseModel):
    source: str
    pages: list[int] | None
    score: float


class AskResponse(BaseModel):
    answer: str


class IngestResponse(BaseModel):
    filename: str
    chunks_stored: int