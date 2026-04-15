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
