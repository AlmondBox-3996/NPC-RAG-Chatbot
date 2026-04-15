import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from npc_rag.api.dependencies import get_dialogue_orchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive local NPC chat demo.")
    parser.add_argument("--npc-id", default="npc_quartermaster_rowan", help="NPC identifier")
    parser.add_argument("--player-id", default="player-001", help="Player identifier")
    parser.add_argument("--debug", action="store_true", help="Show retrieval and orchestration debug info")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    orchestrator = get_dialogue_orchestrator()

    print("NPC chat demo started. Type 'exit' or 'quit' to stop.")
    print(f"NPC: {args.npc_id} | Player: {args.player_id} | Debug: {args.debug}")

    while True:
        try:
            message = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not message:
            continue
        if message.lower() in {"exit", "quit"}:
            print("Session ended.")
            break

        response = orchestrator.answer_with_options(
            player_id=args.player_id,
            npc_id=args.npc_id,
            question=message,
            debug=args.debug,
        )

        print(f"\nNPC: {response.answer}")

        if args.debug and response.debug is not None:
            print("\n[Debug] Applied filters:")
            print(response.debug.applied_filters)
            print("[Debug] Retrieved chunks:")
            for chunk in response.debug.retrieved_chunks:
                print(f"- {chunk.document_id} score={chunk.score} source={chunk.source}")

        if args.debug and response.orchestration is not None:
            print("\n[Debug] Orchestration:")
            print(
                {
                    "intent": response.orchestration.intent,
                    "confidence": response.orchestration.confidence,
                    "steps": response.orchestration.pipeline_steps,
                }
            )


if __name__ == "__main__":
    main()
