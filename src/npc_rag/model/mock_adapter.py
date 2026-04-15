from npc_rag.model.ollama_adapter import GenerationResult


class MockModelAdapter:
    def generate(self, prompt: str) -> GenerationResult:
        del prompt
        return GenerationResult(
            text=(
                "If you're hunting a hidden weapon, search the old watchtower beneath the ridge shrine. "
                "The path only opens for scouts who already mapped Whispering Pass, "
                "and the current unrest means you should move before the raiders seize it."
            ),
            used_mock=True,
        )
