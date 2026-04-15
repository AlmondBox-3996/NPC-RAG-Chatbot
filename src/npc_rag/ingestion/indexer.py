from npc_rag.ingestion.documents import chunk_document, load_lore_documents
from npc_rag.retrieval.vector_store import VectorStore


class LoreIndexer:
    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    def ingest(self, lore_path) -> int:
        documents = load_lore_documents(lore_path)
        chunked_documents = [
            chunk
            for document in documents
            for chunk in chunk_document(document)
        ]

        self.vector_store.upsert_documents(chunked_documents)
        return len(chunked_documents)
