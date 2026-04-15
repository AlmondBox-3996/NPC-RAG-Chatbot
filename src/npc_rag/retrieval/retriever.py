from npc_rag.retrieval.vector_store import VectorStore
from npc_rag.schemas.dialogue import FilteredChunk, RetrievalDebug, RetrievedLore
from npc_rag.state.models import PlayerState, WorldState


class LoreRetriever:
    def __init__(self, vector_store: VectorStore, top_k: int, oversample_factor: int = 4) -> None:
        self.vector_store = vector_store
        self.top_k = top_k
        self.oversample_factor = oversample_factor

    def retrieve(
        self,
        question: str,
        player_state: PlayerState,
        world_state: WorldState,
        debug: bool = False,
    ) -> tuple[list[RetrievedLore], RetrievalDebug | None]:
        candidate_limit = max(self.top_k, self.top_k * self.oversample_factor)
        candidates = self.vector_store.query(question, limit=candidate_limit)
        allowed_spoiler_level = self._allowed_spoiler_level(player_state, world_state)
        discovered_regions = set(player_state.discovery.discovered_regions)
        unlocked_regions = {
            region.region_id
            for region in world_state.regions
            if region.is_unlocked
        }
        accessible_regions = discovered_regions | unlocked_regions
        available_quests = set(player_state.progress.completed_quests) | set(player_state.progress.active_quests)
        owned_items = set(player_state.inventory.owned_items)

        accepted: list[RetrievedLore] = []
        excluded: list[FilteredChunk] = []

        for candidate in candidates:
            exclusion_reasons = self._get_exclusion_reasons(
                candidate=candidate,
                accessible_regions=accessible_regions,
                allowed_spoiler_level=allowed_spoiler_level,
                available_quests=available_quests,
                owned_items=owned_items,
            )
            if exclusion_reasons:
                excluded.append(
                    FilteredChunk(
                        document_id=candidate.document_id,
                        source=candidate.source,
                        score=candidate.score,
                        excluded_by=exclusion_reasons,
                        metadata=candidate.metadata,
                    )
                )
                continue

            accepted.append(candidate)
            if len(accepted) >= self.top_k:
                break

        debug_payload = None
        if debug:
            debug_payload = RetrievalDebug(
                query=question,
                top_k=self.top_k,
                candidate_count=len(candidates),
                returned_count=len(accepted),
                applied_filters={
                    "accessible_regions": sorted(accessible_regions),
                    "completed_quests": player_state.progress.completed_quests,
                    "active_quests": player_state.progress.active_quests,
                    "owned_items": player_state.inventory.owned_items,
                    "allowed_spoiler_level": allowed_spoiler_level,
                },
                retrieved_chunks=accepted,
                excluded_chunks=excluded,
            )

        return accepted, debug_payload

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

    def _split_metadata_values(self, value: object) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, str):
            return {part for part in value.split("|") if part}
        return set()

    def _get_exclusion_reasons(
        self,
        candidate: RetrievedLore,
        accessible_regions: set[str],
        allowed_spoiler_level: int,
        available_quests: set[str],
        owned_items: set[str],
    ) -> list[str]:
        metadata = candidate.metadata
        reasons: list[str] = []

        region_tags = self._split_metadata_values(metadata.get("region_tags"))
        if region_tags and region_tags.isdisjoint(accessible_regions):
            reasons.append("undiscovered_region")

        spoiler_level = int(metadata.get("spoiler_level", 0))
        if spoiler_level > allowed_spoiler_level:
            reasons.append("spoiler_level")

        quest_dependencies = self._split_metadata_values(metadata.get("quest_dependencies"))
        if quest_dependencies and not quest_dependencies.issubset(available_quests):
            reasons.append("quest_progression")

        related_items = self._split_metadata_values(metadata.get("related_items"))
        if related_items and related_items.isdisjoint(owned_items):
            reasons.append("owned_items")

        return reasons
