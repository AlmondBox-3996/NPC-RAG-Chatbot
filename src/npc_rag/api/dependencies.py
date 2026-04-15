from functools import lru_cache

from npc_rag.core.config import Settings, get_settings
from npc_rag.model.mock_adapter import MockModelAdapter
from npc_rag.model.ollama_adapter import ModelAdapter, OllamaModelAdapter
from npc_rag.orchestrator.dialogue_service import DialogueOrchestrator
from npc_rag.retrieval.embedding_service import EmbeddingService
from npc_rag.retrieval.retriever import LoreRetriever
from npc_rag.retrieval.vector_store import ChromaVectorStore
from npc_rag.state.loader import StateLoader


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(settings.embedding_model)


@lru_cache(maxsize=1)
def get_vector_store() -> ChromaVectorStore:
    settings = get_settings()
    settings.vector_db_path.mkdir(parents=True, exist_ok=True)
    return ChromaVectorStore(
        persist_path=str(settings.vector_db_path),
        collection_name=settings.vector_collection_name,
        embedding_service=get_embedding_service(),
    )


@lru_cache(maxsize=1)
def get_state_loader() -> StateLoader:
    settings = get_settings()
    return StateLoader(
        player_state_path=settings.player_state_path,
        world_state_path=settings.world_state_path,
    )


@lru_cache(maxsize=1)
def get_model_adapter() -> ModelAdapter:
    settings: Settings = get_settings()
    fallback = MockModelAdapter() if settings.enable_mock_llm else None
    return OllamaModelAdapter(
        model_name=settings.ollama_model,
        base_url=settings.ollama_base_url,
        fallback_adapter=fallback,
    )


def get_dialogue_orchestrator() -> DialogueOrchestrator:
    settings = get_settings()
    retriever = LoreRetriever(get_vector_store(), top_k=settings.top_k_results)
    return DialogueOrchestrator(
        npc_name=settings.npc_name,
        retriever=retriever,
        state_loader=get_state_loader(),
        model_adapter=get_model_adapter(),
    )
