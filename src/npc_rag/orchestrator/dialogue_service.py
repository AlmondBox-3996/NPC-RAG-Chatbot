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
        player_state = self.state_loader.load_player_state(player_id)
        world_state = self.state_loader.load_world_state()
        lore = self.retriever.retrieve(question)

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
        }

        return DialogueResponse(
            npc_id=npc_id,
            npc_name=self.npc_name,
            answer=generation.text,
            retrieved_lore=lore,
            state_summary=state_summary,
            used_mock_llm=generation.used_mock,
        )
