import json
from pathlib import Path

from npc_rag.state.models import PlayerState, WorldState


class StateLoader:
    def __init__(self, player_state_path: Path, world_state_path: Path) -> None:
        self.player_state_path = player_state_path
        self.world_state_path = world_state_path

    def load_player_state(self, player_id: str) -> PlayerState:
        payload = json.loads(self.player_state_path.read_text(encoding="utf-8"))
        players = payload.get("players", [])
        for player in players:
            if player.get("player_id") == player_id:
                return PlayerState.model_validate(player)
        raise ValueError(f"Player '{player_id}' was not found.")

    def load_world_state(self) -> WorldState:
        payload = json.loads(self.world_state_path.read_text(encoding="utf-8"))
        return WorldState.model_validate(payload)
