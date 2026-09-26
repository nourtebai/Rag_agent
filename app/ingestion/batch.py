from pathlib import Path

from app.ingestion.loader import load_and_chunk


def load_all(data_dir: str = "data") -> list:
    """Charge et chunk tous les PDF d'un dossier."""
    pdf_files = sorted(Path(data_dir).glob("*.pdf"))

    if not pdf_files:
        print(f"Aucun PDF trouvé dans {data_dir}/")
        return []

    all_chunks = []
    for pdf in pdf_files:
        print(f"  {pdf.name}...", end=" ")
        chunks = load_and_chunk(str(pdf))
        print(f"{len(chunks)} chunks")
        all_chunks.extend(chunks)

    return all_chunks