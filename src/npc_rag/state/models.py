from typing import Any

from pydantic import BaseModel


class PlayerState(BaseModel):
    player_id: str
    name: str
    level: int
    completed_quests: list[str]
    known_locations: list[str]
    inventory: list[str]
    flags: dict[str, Any]


class WorldState(BaseModel):
    region: str
    weather: str
    threat_level: str
    active_events: list[str]
    hidden_weapon_hint: str
    npc_context: dict[str, Any]
