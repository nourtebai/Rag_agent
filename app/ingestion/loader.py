from pathlib import Path

from langchain_core.documents import Document
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType


def _clean_metadata(raw: dict, source: str) -> dict:
    """Keep only what we need: file name, page numbers, headings."""
    meta = {"source": source}
    dl = raw.get("dl_meta", {})
    pages = sorted({
        p["page_no"]
        for item in dl.get("doc_items", [])
        for p in item.get("prov", [])
        if "page_no" in p
    })
    if pages:
        meta["pages"] = pages
    if dl.get("headings"):
        meta["headings"] = dl["headings"]
    return meta


def load_and_chunk(file_path: str) -> list[Document]:
    path = Path(file_path)
    loader = DoclingLoader(
        file_path=str(path),
        export_type=ExportType.DOC_CHUNKS,
    )
    return [
        Document(page_content=d.page_content, metadata=_clean_metadata(d.metadata, path.name))
        for d in loader.load()
    ]
