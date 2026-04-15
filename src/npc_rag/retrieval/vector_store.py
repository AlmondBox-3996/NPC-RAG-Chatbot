from abc import ABC, abstractmethod

import chromadb
from chromadb.config import Settings as ChromaSettings

from npc_rag.ingestion.documents import LoreDocument
from npc_rag.retrieval.embedding_service import EmbeddingService
from npc_rag.schemas.dialogue import RetrievedLore


class VectorStore(ABC):
    @abstractmethod
    def upsert_documents(self, documents: list[LoreDocument]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, query_text: str, limit: int) -> list[RetrievedLore]:
        raise NotImplementedError


class ChromaVectorStore(VectorStore):
    def __init__(
        self,
        persist_path: str,
        collection_name: str,
        embedding_service: EmbeddingService,
    ) -> None:
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(
            path=persist_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert_documents(self, documents: list[LoreDocument]) -> None:
        if not documents:
            return

        ids = [document.document_id for document in documents]
        texts = [document.content for document in documents]
        metadatas = [
            {
                **document.metadata,
                "source": document.source,
                "document_id": document.document_id,
            }
            for document in documents
        ]
        embeddings = self.embedding_service.embed_documents(texts)

        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    def query(self, query_text: str, limit: int) -> list[RetrievedLore]:
        query_embedding = self.embedding_service.embed_query(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        retrieved: list[RetrievedLore] = []

        for document, metadata in zip(documents, metadatas):
            metadata = metadata or {}
            retrieved.append(
                RetrievedLore(
                    document_id=str(metadata.get("document_id", "unknown")),
                    source=str(metadata.get("source", "unknown")),
                    content=document,
                    metadata=metadata,
                )
            )

        return retrieved
