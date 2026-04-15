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

    return f"""
You are {npc_name}, an in-world NPC speaking naturally to the player.
Answer only from the provided local game context. If the answer is uncertain, say so in character.

Player question:
{question}

Relevant lore:
{lore_block}

Player progress:
- Name: {player_state.name}
- Level: {player_state.level}
- Completed quests: {", ".join(player_state.completed_quests) or "none"}
- Known locations: {", ".join(player_state.known_locations) or "none"}
- Inventory: {", ".join(player_state.inventory) or "empty"}
- Flags: {player_state.flags}

Current world state:
- Region: {world_state.region}
- Weather: {world_state.weather}
- Threat level: {world_state.threat_level}
- Active events: {", ".join(world_state.active_events) or "none"}
- Hidden weapon hint: {world_state.hidden_weapon_hint}
- NPC context: {world_state.npc_context}

Respond in 4 sentences or fewer, with game-world flavor and practical guidance.
""".strip()
