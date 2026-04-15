from abc import ABC, abstractmethod
from dataclasses import dataclass

import ollama


@dataclass(slots=True)
class GenerationResult:
    text: str
    used_mock: bool


class ModelAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> GenerationResult:
        raise NotImplementedError


class OllamaModelAdapter(ModelAdapter):
    def __init__(self, model_name: str, base_url: str, fallback_adapter: ModelAdapter | None = None) -> None:
        self.model_name = model_name
        self.client = ollama.Client(host=base_url)
        self.fallback_adapter = fallback_adapter

    def generate(self, prompt: str) -> GenerationResult:
        try:
            response = self.client.generate(model=self.model_name, prompt=prompt)
            return GenerationResult(text=response["response"].strip(), used_mock=False)
        except Exception:
            if self.fallback_adapter is None:
                raise
            return self.fallback_adapter.generate(prompt)
