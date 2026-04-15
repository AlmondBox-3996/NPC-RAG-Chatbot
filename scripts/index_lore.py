import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from npc_rag.api.dependencies import get_vector_store
from npc_rag.core.config import get_settings
from npc_rag.ingestion.indexer import LoreIndexer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Index local lore documents into the configured vector store.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing collection before indexing.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = get_settings()
    indexer = LoreIndexer(get_vector_store())
    result = indexer.ingest(settings.lore_path, reset=args.reset)

    action = "Reindexed" if result.reset_applied else "Indexed"
    print(
        f"{action} {result.indexed_documents} lore documents into "
        f"{result.indexed_chunks} chunks in {settings.vector_db_provider} "
        f"collection '{settings.vector_collection_name}'."
    )
    print("Indexing is idempotent: stable chunk IDs are upserted on repeat runs.")


if __name__ == "__main__":
    main()
