import json
from pathlib import Path

from npc_rag.state.derived_context import DerivedContextBuilder
from npc_rag.state.models import DerivedContext, PlayerState, WorldState


class StateLoader:
    def __init__(
        self,
        player_state_path: Path,
        world_state_path: Path,
        npc_data_path: Path,
        item_data_path: Path,
    ) -> None:
        self.player_state_path = player_state_path
        self.world_state_path = world_state_path
        self.derived_context_builder = DerivedContextBuilder(
            npc_data_path=npc_data_path,
            item_data_path=item_data_path,
        )

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

    def build_derived_context(
        self,
        player_state: PlayerState,
        world_state: WorldState,
        npc_id: str,
    ) -> DerivedContext:
        return self.derived_context_builder.build(
            player_state=player_state,
            world_state=world_state,
            npc_id=npc_id,
        )
