from typing import Any

from pydantic import BaseModel, Field


class PlayerProgress(BaseModel):
    main_story_stage: str
    completed_quests: list[str]
    active_quests: list[str]
    failed_quests: list[str]


class PlayerInventory(BaseModel):
    currencies: dict[str, int]
    owned_items: list[str]
    equipped_items: list[str]


class PlayerDiscovery(BaseModel):
    discovered_regions: list[str]
    visited_dungeons: list[str]
    known_npcs: list[str]


class PlayerState(BaseModel):
    player_id: str
    name: str
    player_class: str = Field(alias="class")
    level: int
    progress: PlayerProgress
    inventory: PlayerInventory
    discovery: PlayerDiscovery
    flags: dict[str, Any]


class RegionState(BaseModel):
    region_id: str
    name: str
    tags: list[str]
    is_unlocked: bool
    threat_level: str


class BossState(BaseModel):
    boss_id: str
    name: str
    region_id: str
    status: str
    gates_region_unlock: str | None


class WorldEvent(BaseModel):
    event_id: str
    description: str
    affected_regions: list[str]


class WorldState(BaseModel):
    world_id: str
    time: dict[str, Any]
    regions: list[RegionState]
    bosses: list[BossState]
    active_events: list[WorldEvent]
    global_flags: dict[str, Any]


class NpcPersonality(BaseModel):
    traits: list[str]
    speaking_style: str


class NpcKnowledgeBoundaries(BaseModel):
    knows_about: list[str]
    refuses_to_reveal_above_spoiler_level: int
    requires_completed_quests_for_full_hint: list[str]
    forbidden_topics: list[str]


class NpcState(BaseModel):
    npc_id: str
    name: str
    role: str
    home_region: str
    region_tags: list[str]
    spoiler_level: int
    personality: NpcPersonality
    knowledge_boundaries: NpcKnowledgeBoundaries


class WorldStatus(BaseModel):
    unlocked_dungeons: list[str]
    locked_dungeons: list[str]
    bosses_alive: list[str]
    bosses_dead: list[str]
    claimed_items: list[str]
    unclaimed_items: list[str]


class PlayerKnowledge(BaseModel):
    accessible_regions: list[str]
    completed_quests: list[str]
    active_quests: list[str]
    owned_items: list[str]
    allowed_spoiler_level: int
    allowed_lore_topics: list[str]
    progression_stage: str


class NpcRevealPolicy(BaseModel):
    npc_id: str
    npc_name: str
    reveal_spoiler_level: int
    known_topics: list[str]
    blocked_topics: list[str]
    full_hint_unlocked: bool
    reveal_style: str
    archetype: str


class DerivedContext(BaseModel):
    player_knowledge: PlayerKnowledge
    npc_reveal_policy: NpcRevealPolicy
    world_status: WorldStatus
