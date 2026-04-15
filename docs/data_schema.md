# Data Schema

The sample data layer uses local JSON because it is easy to inspect, patch, and ship with a Windows-first prototype. Each file is structured so the orchestration layer can apply deterministic filters before prompt construction.

## Files

- `data/lore/lore_documents.json`: structured lore records for retrieval and spoiler-aware filtering.
- `data/quests.json`: quest definitions, region relevance, and prerequisite chains.
- `data/items.json`: weapon metadata, hidden item gating, and ownership requirements.
- `data/npcs.json`: personalities plus explicit knowledge boundaries for hint generation.
- `data/state/player_state.json`: per-player progress, inventory, and discovered content.
- `data/state/world_state.json`: global world progression, bosses, active events, and unlock states.

## Core fields

- `region_tags`: lets the system filter records to the player's discovered or currently relevant regions.
- `spoiler_level`: lets the application suppress endgame content for early-game players or NPCs.
- `quest_dependencies` and `prerequisites.required_completed_quests`: make progression checks explicit.
- `ownership_conditions`: allows item hints and grants to depend on quests, flags, owned items, and unlocked regions.
- `knowledge_boundaries`: prevents NPCs from acting omniscient and supports persona-aware responses.

## Filtering model

A simple local filter pass can be applied before sending any context to the LLM:

1. Region filter:
   Keep records where `region_tags` overlap with `player.discovery.discovered_regions`, unless the content is intentionally global.

2. Quest filter:
   Keep records whose `quest_dependencies` are empty or fully satisfied by `player.progress.completed_quests`.

3. Ownership filter:
   For item availability, require all values in `ownership_conditions.required_owned_items` to exist in `player.inventory.owned_items`.

4. Spoiler filter:
   Drop records above the allowed spoiler ceiling for the player's progress or the speaking NPC's `refuses_to_reveal_above_spoiler_level`.

## Why JSON first

JSON is enough for local prototyping and test fixtures, and the schema maps cleanly to SQLite later:

- `lore_documents`, `quests`, `items`, `npcs`, `players`, `regions`, `bosses`
- join tables for `region_tags`, `completed_quests`, and `owned_items`
- indexed filter columns for `spoiler_level`, `region_id`, and `quest_id`

That means you can keep the same domain model while moving from file-backed development to a more performant embedded database when the game runtime needs it.
