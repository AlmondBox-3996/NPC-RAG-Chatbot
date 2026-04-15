from npc_rag.schemas.dialogue import RetrievedLore
from npc_rag.state.models import PlayerState, WorldState


def build_npc_prompt(
    npc_name: str,
    question: str,
    lore_context: list[RetrievedLore],
    player_state: PlayerState,
    world_state: WorldState,
) -> str:
    lore_block = "\n\n".join(
        f"[{item.source}] {item.content}"
        for item in lore_context
    ) or "No lore passages were retrieved."
    unlocked_regions = [region.name for region in world_state.regions if region.is_unlocked]
    active_event_descriptions = [event.description for event in world_state.active_events]
    boss_summaries = [f"{boss.name} ({boss.status})" for boss in world_state.bosses]

    return f"""
You are {npc_name}, an in-world NPC speaking naturally to the player.
Answer only from the provided local game context. If the answer is uncertain, say so in character.

Player question:
{question}

Relevant lore:
{lore_block}

Player progress:
- Name: {player_state.name}
- Class: {player_state.player_class}
- Level: {player_state.level}
- Completed quests: {", ".join(player_state.progress.completed_quests) or "none"}
- Active quests: {", ".join(player_state.progress.active_quests) or "none"}
- Discovered regions: {", ".join(player_state.discovery.discovered_regions) or "none"}
- Inventory: {", ".join(player_state.inventory.owned_items) or "empty"}
- Flags: {player_state.flags}

Current world state:
- Unlocked regions: {", ".join(unlocked_regions) or "none"}
- Active events: {", ".join(active_event_descriptions) or "none"}
- Bosses: {", ".join(boss_summaries) or "none"}
- Global flags: {world_state.global_flags}

Respond in 4 sentences or fewer, with game-world flavor and practical guidance.
""".strip()
