from npc_rag.schemas.dialogue import RetrievedLore
from npc_rag.state.models import DerivedContext, PlayerState, WorldState


NPC_STYLE_GUIDANCE = {
    "cryptic_guide": {
        "label": "cryptic guide",
        "voice": "Speak in layered hints, omen-like phrasing, and partial directions without becoming vague or useless.",
    },
    "helpful_villager": {
        "label": "helpful villager",
        "voice": "Speak plainly, kindly, and practically, favoring clear directions over mystery.",
    },
    "blacksmith": {
        "label": "blacksmith",
        "voice": "Speak bluntly and concretely, with a craftsperson's focus on gear, risk, and what is worth carrying.",
    },
    "scholar": {
        "label": "scholar",
        "voice": "Speak precisely and analytically, grounding claims in records, history, and observed detail.",
    },
}


def build_system_prompt(npc_name: str, derived_context: DerivedContext) -> str:
    style = NPC_STYLE_GUIDANCE.get(
        derived_context.npc_reveal_policy.archetype,
        NPC_STYLE_GUIDANCE["helpful_villager"],
    )
    hint_mode = (
        "Give direct but still in-world guidance."
        if derived_context.npc_reveal_policy.full_hint_unlocked
        else "Give hint-based guidance instead of explicit coordinates, final solutions, or hidden-step walkthroughs."
    )

    return f"""
You are {npc_name}, an NPC in a local-only RPG dialogue system.

Non-negotiable rules:
- Use only the supplied lore, player state, world state, and reveal policy.
- Do not hallucinate people, places, quest steps, item locations, or mechanics that are not in the provided context.
- Do not reveal spoilers above spoiler level {derived_context.npc_reveal_policy.reveal_spoiler_level}.
- Do not discuss blocked topics: {", ".join(derived_context.npc_reveal_policy.blocked_topics) or "none"}.
- If the answer is unsupported by context, say that you do not know or cannot confirm it.
- Never present guesses as facts.

NPC style:
- Archetype: {style["label"]}
- Voice guidance: {style["voice"]}
- Local speaking style: {derived_context.npc_reveal_policy.reveal_style}

Disclosure behavior:
- {hint_mode}
- Adapt detail to progression stage: {derived_context.player_knowledge.progression_stage}.
- Only reveal topics this NPC is allowed to know: {", ".join(derived_context.npc_reveal_policy.known_topics) or "none"}.
- Keep the response immersive, grounded, and no longer than 4 sentences.
""".strip()


def build_context_prompt(
    question: str,
    lore_context: list[RetrievedLore],
    player_state: PlayerState,
    world_state: WorldState,
    derived_context: DerivedContext,
) -> str:
    lore_block = "\n\n".join(
        f"[{item.document_id} | score={item.score}] {item.content}"
        for item in lore_context
    ) or "No lore passages were retrieved."

    unlocked_regions = [region.name for region in world_state.regions if region.is_unlocked]
    active_event_descriptions = [event.description for event in world_state.active_events]
    boss_summaries = [f"{boss.name} ({boss.status})" for boss in world_state.bosses]

    return f"""
Player query:
{question}

Retrieved lore:
{lore_block}

Player state summary:
- Name: {player_state.name}
- Class: {player_state.player_class}
- Level: {player_state.level}
- Completed quests: {", ".join(player_state.progress.completed_quests) or "none"}
- Active quests: {", ".join(player_state.progress.active_quests) or "none"}
- Discovered regions: {", ".join(player_state.discovery.discovered_regions) or "none"}
- Owned items: {", ".join(player_state.inventory.owned_items) or "none"}
- Progression stage: {derived_context.player_knowledge.progression_stage}
- Allowed spoiler level: {derived_context.player_knowledge.allowed_spoiler_level}

World state summary:
- Unlocked regions: {", ".join(unlocked_regions) or "none"}
- Locked dungeons: {", ".join(derived_context.world_status.locked_dungeons) or "none"}
- Active events: {", ".join(active_event_descriptions) or "none"}
- Bosses alive: {", ".join(derived_context.world_status.bosses_alive) or "none"}
- Bosses dead: {", ".join(derived_context.world_status.bosses_dead) or "none"}
- Claimed items: {", ".join(derived_context.world_status.claimed_items) or "none"}

Reveal constraints:
- NPC spoiler ceiling: {derived_context.npc_reveal_policy.reveal_spoiler_level}
- Full hint unlocked: {derived_context.npc_reveal_policy.full_hint_unlocked}
- Known topics: {", ".join(derived_context.npc_reveal_policy.known_topics) or "none"}
- Blocked topics: {", ".join(derived_context.npc_reveal_policy.blocked_topics) or "none"}
""".strip()


def build_npc_prompt(
    npc_name: str,
    question: str,
    lore_context: list[RetrievedLore],
    player_state: PlayerState,
    world_state: WorldState,
    derived_context: DerivedContext,
) -> str:
    system_prompt = build_system_prompt(npc_name=npc_name, derived_context=derived_context)
    context_prompt = build_context_prompt(
        question=question,
        lore_context=lore_context,
        player_state=player_state,
        world_state=world_state,
        derived_context=derived_context,
    )
    return f"{system_prompt}\n\nContext:\n{context_prompt}\n\nAnswer as the NPC now."


def build_prompt_messages(
    npc_name: str,
    question: str,
    lore_context: list[RetrievedLore],
    player_state: PlayerState,
    world_state: WorldState,
    derived_context: DerivedContext,
) -> tuple[str, str]:
    system_prompt = build_system_prompt(npc_name=npc_name, derived_context=derived_context)
    prompt = build_context_prompt(
        question=question,
        lore_context=lore_context,
        player_state=player_state,
        world_state=world_state,
        derived_context=derived_context,
    )
    return system_prompt, prompt
