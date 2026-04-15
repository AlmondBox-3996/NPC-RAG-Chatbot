# NPC RAG Chatbot

Local-only RAG-powered NPC dialogue backend for a game. The stack is designed for Windows development with FastAPI, ChromaDB, sentence-transformers, Ollama, and JSON-based local state.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/ingest_lore.py
uvicorn src.npc_rag.main:app --reload
```

## Example request

```http
POST /api/v1/dialogue/query
Content-Type: application/json

{
  "player_id": "player-001",
  "npc_id": "quartermaster_rowan",
  "question": "Where can I find a hidden weapon?"
}
```

## Architecture

- `ingestion`: loads lore documents, chunks them, and writes them into the vector store.
- `retrieval`: embeds queries and retrieves the most relevant lore passages.
- `state`: loads player and world state from local JSON files.
- `orchestrator`: combines retrieval results with state and builds the final prompt.
- `model`: talks to Ollama and falls back to a deterministic mock generator when needed.
- `api`: FastAPI endpoints and dependency wiring.

This keeps retrieval, state, and model access isolated so you can later swap JSON for SQLite, ChromaDB for FAISS, or the HTTP API for a native game engine bridge without rewriting the rest of the system.

## Data Layer

The project now includes a structured local data layer for:

- 5 lore documents with spoiler levels and region tags
- 3 quests with prerequisite chains
- 4 weapons with hidden-item ownership conditions
- 3 NPCs with personalities and knowledge boundaries
- player and world state with discovered regions, bosses, and unlock state

See [docs/data_schema.md](/d:/Codar/NPC-RAG-Chatbot/docs/data_schema.md) for the schema and filtering model.
