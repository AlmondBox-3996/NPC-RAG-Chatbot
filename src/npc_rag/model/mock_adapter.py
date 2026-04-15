import hashlib

from npc_rag.model.ollama_adapter import GenerationResult


class MockModelAdapter:
    def generate(self, prompt: str, system_prompt: str, temperature: float) -> GenerationResult:
        digest = hashlib.sha1(f"{system_prompt}\n{prompt}\n{temperature:.2f}".encode("utf-8")).hexdigest()[:8]
        return GenerationResult(
            text=(
                "From what I can confirm, the safest lead points toward the old watchtower above the shrine road. "
                "Anyone chasing hidden steel should first secure the pass and follow the warden markers rather than hunt blindly. "
                f"Mock trace {digest}."
            ),
            used_mock=True,
        )
