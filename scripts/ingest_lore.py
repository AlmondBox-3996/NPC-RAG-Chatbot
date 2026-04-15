from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from npc_rag.api.dependencies import get_vector_store
from npc_rag.core.config import get_settings
from npc_rag.ingestion.indexer import LoreIndexer


def main() -> None:
    settings = get_settings()
    indexer = LoreIndexer(get_vector_store())
    result = indexer.ingest(settings.lore_path)
    print(
        f"Indexed {result.indexed_documents} lore documents into "
        f"{result.indexed_chunks} chunks in {settings.vector_db_provider}."
    )


if __name__ == "__main__":
    main()
