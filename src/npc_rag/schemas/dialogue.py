from typing import Any

from pydantic import BaseModel, Field


class DialogueQuery(BaseModel):
    player_id: str = Field(..., examples=["player-001"])
    npc_id: str = Field(..., examples=["quartermaster_rowan"])
    question: str = Field(..., examples=["Where can I find a hidden weapon?"])
    debug: bool = Field(default=False, examples=[True])


class RetrievedLore(BaseModel):
    document_id: str
    source: str
    content: str
    metadata: dict[str, Any]
    score: float | None = None


class FilteredChunk(BaseModel):
    document_id: str
    source: str
    score: float | None = None
    excluded_by: list[str]
    metadata: dict[str, Any]


class RetrievalDebug(BaseModel):
    query: str
    top_k: int
    candidate_count: int
    returned_count: int
    applied_filters: dict[str, Any]
    retrieved_chunks: list[RetrievedLore]
    excluded_chunks: list[FilteredChunk]


class OrchestrationDebug(BaseModel):
    intent: str
    confidence: float
    cues: list[str]
    pipeline_steps: list[str]
    system_prompt_preview: str | None = None


class DialogueResponse(BaseModel):
    npc_id: str
    npc_name: str
    answer: str
    retrieved_lore: list[RetrievedLore]
    state_summary: dict[str, Any]
    used_mock_llm: bool
    debug: RetrievalDebug | None = None
    orchestration: OrchestrationDebug | None = None
