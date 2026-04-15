import json
from pathlib import Path

from npc_rag.state.models import (
    DerivedContext,
    NpcRevealPolicy,
    NpcState,
    PlayerKnowledge,
    PlayerState,
    WorldState,
    WorldStatus,
)


class DerivedContextBuilder:
    def __init__(self, npc_data_path: Path, item_data_path: Path) -> None:
        self.npc_data_path = npc_data_path
        self.item_data_path = item_data_path

    def load_npc_state(self, npc_id: str) -> NpcState:
        payload = json.loads(self.npc_data_path.read_text(encoding="utf-8"))
        for npc in payload.get("npcs", []):
            if npc.get("npc_id") == npc_id:
                return NpcState.model_validate(npc)
        raise ValueError(f"NPC '{npc_id}' was not found.")

    def build(self, player_state: PlayerState, world_state: WorldState, npc_id: str) -> DerivedContext:
        npc_state = self.load_npc_state(npc_id)
        allowed_spoiler_level = self._allowed_spoiler_level(player_state, world_state)
        accessible_regions = self._accessible_regions(player_state, world_state)
        progression_stage = self._progression_stage(player_state, world_state)
        owned_items = list(player_state.inventory.owned_items)
        known_topics = list(npc_state.knowledge_boundaries.knows_about)

        player_knowledge = PlayerKnowledge(
            accessible_regions=accessible_regions,
            completed_quests=list(player_state.progress.completed_quests),
            active_quests=list(player_state.progress.active_quests),
            owned_items=owned_items,
            allowed_spoiler_level=allowed_spoiler_level,
            allowed_lore_topics=known_topics[:],
            progression_stage=progression_stage,
        )

        full_hint_unlocked = set(npc_state.knowledge_boundaries.requires_completed_quests_for_full_hint).issubset(
            set(player_state.progress.completed_quests)
        )
        reveal_spoiler_level = min(
            allowed_spoiler_level,
            npc_state.knowledge_boundaries.refuses_to_reveal_above_spoiler_level,
        )

        npc_reveal_policy = NpcRevealPolicy(
            npc_id=npc_state.npc_id,
            npc_name=npc_state.name,
            reveal_spoiler_level=reveal_spoiler_level,
            known_topics=known_topics,
            blocked_topics=list(npc_state.knowledge_boundaries.forbidden_topics),
            full_hint_unlocked=full_hint_unlocked,
            reveal_style=npc_state.personality.speaking_style,
        )

        world_status = self._world_status(player_state, world_state)

        return DerivedContext(
            player_knowledge=player_knowledge,
            npc_reveal_policy=npc_reveal_policy,
            world_status=world_status,
        )

    def _accessible_regions(self, player_state: PlayerState, world_state: WorldState) -> list[str]:
        discovered = set(player_state.discovery.discovered_regions)
        unlocked = {region.region_id for region in world_state.regions if region.is_unlocked}
        return sorted(discovered | unlocked)

    def _allowed_spoiler_level(self, player_state: PlayerState, world_state: WorldState) -> int:
        completed = set(player_state.progress.completed_quests)
        active = set(player_state.progress.active_quests)
        unlocked_regions = {region.region_id for region in world_state.regions if region.is_unlocked}

        if "q_archive_below_tide" in completed or "sunken_archive" in unlocked_regions:
            return 3
        if "q_shrine_of_embers" in completed or "q_shrine_of_embers" in active or "ridge_shrine" in unlocked_regions:
            return 2
        if "q_scouts_ledger" in completed or "q_scouts_ledger" in active or "whispering_pass" in player_state.discovery.discovered_regions:
            return 1
        return 0

    def _progression_stage(self, player_state: PlayerState, world_state: WorldState) -> str:
        allowed_spoiler_level = self._allowed_spoiler_level(player_state, world_state)
        if allowed_spoiler_level >= 3:
            return "endgame"
        if allowed_spoiler_level == 2:
            return "midgame"
        if allowed_spoiler_level == 1:
            return "early_midgame"
        return "early_game"

    def _world_status(self, player_state: PlayerState, world_state: WorldState) -> WorldStatus:
        unlocked_dungeons: list[str] = []
        locked_dungeons: list[str] = []
        for region in world_state.regions:
            if "dungeon" in region.tags or "ruins" in region.tags or "shrine" in region.tags:
                if region.is_unlocked:
                    unlocked_dungeons.append(region.region_id)
                else:
                    locked_dungeons.append(region.region_id)

        bosses_alive = [boss.boss_id for boss in world_state.bosses if boss.status == "alive"]
        bosses_dead = [boss.boss_id for boss in world_state.bosses if boss.status == "dead"]

        items_payload = json.loads(self.item_data_path.read_text(encoding="utf-8"))
        item_ids = [str(item["item_id"]) for item in items_payload.get("items", [])]
        claimed_items = [item_id for item_id in item_ids if item_id in player_state.inventory.owned_items]
        unclaimed_items = [item_id for item_id in item_ids if item_id not in player_state.inventory.owned_items]

        return WorldStatus(
            unlocked_dungeons=sorted(unlocked_dungeons),
            locked_dungeons=sorted(locked_dungeons),
            bosses_alive=sorted(bosses_alive),
            bosses_dead=sorted(bosses_dead),
            claimed_items=sorted(claimed_items),
            unclaimed_items=sorted(unclaimed_items),
        )
