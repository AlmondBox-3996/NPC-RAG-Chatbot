from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class LoreDocument:
    document_id: str
    source: str
    content: str
    metadata: dict


def load_lore_documents(lore_path: Path) -> list[LoreDocument]:
    documents: list[LoreDocument] = []

    for file_path in sorted(lore_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()
        if not text:
            continue

        documents.append(
            LoreDocument(
                document_id=file_path.stem,
                source=file_path.name,
                content=text,
                metadata={"category": "lore", "filename": file_path.name},
            )
        )

    return documents


def chunk_document(document: LoreDocument, chunk_size: int = 500, overlap: int = 75) -> list[LoreDocument]:
    chunks: list[LoreDocument] = []
    text = document.content
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                LoreDocument(
                    document_id=f"{document.document_id}-chunk-{index}",
                    source=document.source,
                    content=chunk_text,
                    metadata={**document.metadata, "chunk_index": index},
                )
            )
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
        index += 1

    return chunks
