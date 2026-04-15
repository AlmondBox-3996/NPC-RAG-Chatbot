from npc_rag.model.ollama_adapter import GenerationResult, ModelAdapter
from npc_rag.orchestrator.prompt_builder import build_npc_prompt
from npc_rag.retrieval.retriever import LoreRetriever
from npc_rag.schemas.dialogue import DialogueResponse
from npc_rag.state.loader import StateLoader


class DialogueOrchestrator:
    def __init__(
        self,
        npc_name: str,
        retriever: LoreRetriever,
        state_loader: StateLoader,
        model_adapter: ModelAdapter,
    ) -> None:
        self.npc_name = npc_name
        self.retriever = retriever
        self.state_loader = state_loader
        self.model_adapter = model_adapter

    def answer(self, player_id: str, npc_id: str, question: str) -> DialogueResponse:
        return self.answer_with_options(player_id=player_id, npc_id=npc_id, question=question, debug=False)

    def answer_with_options(
        self,
        player_id: str,
        npc_id: str,
        question: str,
        debug: bool = False,
    ) -> DialogueResponse:
        player_state = self.state_loader.load_player_state(player_id)
        world_state = self.state_loader.load_world_state()
        derived_context = self.state_loader.build_derived_context(
            player_state=player_state,
            world_state=world_state,
            npc_id=npc_id,
        )
        lore, retrieval_debug = self.retriever.retrieve(
            question=question,
            player_state=player_state,
            world_state=world_state,
            debug=debug,
        )

        prompt = build_npc_prompt(
            npc_name=self.npc_name,
            question=question,
            lore_context=lore,
            player_state=player_state,
            world_state=world_state,
        )
        generation: GenerationResult = self.model_adapter.generate(prompt)

        state_summary = {
            "player_level": player_state.level,
            "completed_quests": player_state.progress.completed_quests,
            "active_quests": player_state.progress.active_quests,
            "discovered_regions": player_state.discovery.discovered_regions,
            "owned_items": player_state.inventory.owned_items,
            "unlocked_regions": [region.region_id for region in world_state.regions if region.is_unlocked],
            "active_events": [event.description for event in world_state.active_events],
            "progression_stage": derived_context.player_knowledge.progression_stage,
            "allowed_spoiler_level": derived_context.player_knowledge.allowed_spoiler_level,
            "npc_reveal_spoiler_level": derived_context.npc_reveal_policy.reveal_spoiler_level,
            "npc_full_hint_unlocked": derived_context.npc_reveal_policy.full_hint_unlocked,
            "unlocked_dungeons": derived_context.world_status.unlocked_dungeons,
            "locked_dungeons": derived_context.world_status.locked_dungeons,
            "bosses_alive": derived_context.world_status.bosses_alive,
            "bosses_dead": derived_context.world_status.bosses_dead,
            "claimed_items": derived_context.world_status.claimed_items,
        }

        return DialogueResponse(
            npc_id=npc_id,
            npc_name=self.npc_name,
            answer=generation.text,
            retrieved_lore=lore,
            state_summary=state_summary,
            used_mock_llm=generation.used_mock,
            debug=retrieval_debug,
        )
