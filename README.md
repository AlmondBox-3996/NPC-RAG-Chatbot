# NPC RAG Chatbot

Local-only RAG-powered NPC dialogue backend for a game. The stack is designed for Windows development with FastAPI, ChromaDB, sentence-transformers, Ollama, and JSON-based local state.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/index_lore.py
uvicorn src.npc_rag.main:app --reload
```

To rebuild the vector collection from scratch:

```powershell
python scripts/index_lore.py --reset
```

## Example request

```http
POST /api/v1/dialogue/query
Content-Type: application/json

{
  "player_id": "player-001",
  "npc_id": "quartermaster_rowan",
  "question": "Where can I find a hidden weapon?",
  "debug": true
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

## State Handling

The state layer now does two jobs:

- load raw player state such as level, inventory, completed quests, and discovered regions
- load world state such as dungeon unlocks, boss status, and claimed items

It also derives runtime facts for dialogue orchestration:

- what the player is allowed to know right now
- what an NPC should reveal based on their knowledge boundaries
- the current progression stage

## Retrieval

The retrieval layer performs:

- semantic vector search over indexed lore chunks
- metadata filtering for discovered regions, spoiler level, and quest progression
- top-k ranking based on vector similarity order after filtering
- optional debug output with retrieved and excluded chunks

Example debug payload shape:

```json
{
  "retrieved_lore": [
    {
      "document_id": "lore_watchtower_cache-chunk-0-a1b2c3d4e5f6",
      "source": "lore_documents.json",
      "content": "During the last siege, the wardens sealed reserve arms beneath the watchtower...",
      "metadata": {
        "region": "whispering_pass",
        "quest": "",
        "item": "",
        "spoiler_level": 1,
        "npc_relevance": "npc_quartermaster_rowan"
      },
      "score": 0.214
    }
  ],
  "debug": {
    "query": "Where can I find a hidden weapon?",
    "top_k": 4,
    "candidate_count": 5,
    "returned_count": 2,
    "applied_filters": {
      "accessible_regions": ["market_square", "red_hollow", "whispering_pass"],
      "completed_quests": ["q_scouts_ledger"],
      "active_quests": ["q_shrine_of_embers"],
      "owned_items": ["itm_watcher_sabre"],
      "allowed_spoiler_level": 2
    },
    "excluded_chunks": [
      {
        "document_id": "lore_sunken_archive-chunk-0-ff00aa11bb22",
        "excluded_by": ["undiscovered_region", "spoiler_level", "quest_progression"]
      }
    ]
  }
}
```

## Prompt System

The prompt builder now combines:

- a strict system prompt with no-hallucination and no-spoiler rules
- NPC archetype style guidance
- retrieved lore
- player state summary
- world state summary
- progression-aware reveal constraints

Supported archetypes:

- `cryptic_guide`
- `helpful_villager`
- `blacksmith`
- `scholar`

Example system prompt shape:

```text
You are Quartermaster Rowan, an NPC in a local-only RPG dialogue system.

Non-negotiable rules:
- Use only the supplied lore, player state, world state, and reveal policy.
- Do not hallucinate people, places, quest steps, item locations, or mechanics that are not in the provided context.
- Do not reveal spoilers above spoiler level 1.
- If the answer is unsupported by context, say that you do not know or cannot confirm it.

NPC style:
- Archetype: blacksmith
- Voice guidance: Speak bluntly and concretely, with a craftsperson's focus on gear, risk, and what is worth carrying.
```

Example full prompt shape:

```text
You are Sister Elira, an NPC in a local-only RPG dialogue system.
...

Context:
Player query:
Where can I find a hidden weapon?

Retrieved lore:
[lore_shrine_embers-chunk-0-...] The Ridge Shrine was built with a concealed reliquary...

Player state summary:
- Level: 12
- Completed quests: q_scouts_ledger
- Active quests: q_shrine_of_embers
- Progression stage: midgame

World state summary:
- Locked dungeons: ridge_shrine, sunken_archive
- Bosses alive: boss_ash_marrow

Reveal constraints:
- NPC spoiler ceiling: 2
- Full hint unlocked: false

Answer as the NPC now.
```

## Model Adapter

The model layer is local-only and swappable:

- `OllamaModelAdapter` calls the configured local Ollama model
- `MockModelAdapter` returns deterministic test responses with no cloud dependency

Environment controls:

- `OLLAMA_MODEL`
- `OLLAMA_BASE_URL`
- `LLM_TEMPERATURE`
- `ENABLE_MOCK_LLM`

Adapter contract:

```python
generate(prompt, system_prompt, temperature)
```

This keeps the orchestration layer independent from the underlying local model runtime.
