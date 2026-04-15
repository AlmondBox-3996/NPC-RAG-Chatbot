from npc_rag.retrieval.vector_store import VectorStore
from npc_rag.schemas.dialogue import RetrievedLore


class LoreRetriever:
    def __init__(self, vector_store: VectorStore, top_k: int) -> None:
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, question: str) -> list[RetrievedLore]:
        return self.vector_store.query(question, limit=self.top_k)
