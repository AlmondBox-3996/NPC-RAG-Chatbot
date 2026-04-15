from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="NPC RAG Chatbot", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    vector_db_provider: str = Field(default="chromadb", alias="VECTOR_DB_PROVIDER")
    vector_db_path: Path = Field(default=Path("./data/chromadb"), alias="VECTOR_DB_PATH")
    vector_collection_name: str = Field(default="game_lore", alias="VECTOR_COLLECTION_NAME")

    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    ollama_model: str = Field(default="llama3.1:8b", alias="OLLAMA_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    enable_mock_llm: bool = Field(default=True, alias="ENABLE_MOCK_LLM")

    player_state_path: Path = Field(default=Path("./data/state/player_state.json"), alias="PLAYER_STATE_PATH")
    world_state_path: Path = Field(default=Path("./data/state/world_state.json"), alias="WORLD_STATE_PATH")
    lore_path: Path = Field(default=Path("./data/lore"), alias="LORE_PATH")
    npc_data_path: Path = Field(default=Path("./data/npcs.json"), alias="NPC_DATA_PATH")
    item_data_path: Path = Field(default=Path("./data/items.json"), alias="ITEM_DATA_PATH")

    top_k_results: int = Field(default=4, alias="TOP_K_RESULTS")
    npc_name: str = Field(default="Quartermaster Rowan", alias="NPC_NAME")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
