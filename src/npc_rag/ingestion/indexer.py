from dataclasses import dataclass
from pathlib import Path

from npc_rag.ingestion.documents import chunk_document, load_lore_documents
from npc_rag.retrieval.vector_store import VectorStore


@dataclass(slots=True)
class IndexingResult:
    indexed_documents: int
    indexed_chunks: int
    reset_applied: bool


class LoreIndexer:
    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def ingest(self, lore_path: Path, reset: bool = False) -> IndexingResult:
        if reset:
            self.vector_store.reset()

        documents = load_lore_documents(lore_path)
        chunked_documents = [
            chunk
            for document in documents
            for chunk in chunk_document(document)
        ]

        self.vector_store.upsert_documents(chunked_documents)
        return IndexingResult(
            indexed_documents=len(documents),
            indexed_chunks=len(chunked_documents),
            reset_applied=reset,
        )
