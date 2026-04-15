from typing import Any

from pydantic import BaseModel, Field


class DialogueQuery(BaseModel):
    player_id: str = Field(..., examples=["player-001"])
    npc_id: str = Field(..., examples=["quartermaster_rowan"])
    question: str = Field(..., examples=["Where can I find a hidden weapon?"])


class RetrievedLore(BaseModel):
    document_id: str
    source: str
    content: str
    metadata: dict[str, Any]


class DialogueResponse(BaseModel):
    npc_id: str
    npc_name: str
    answer: str
    retrieved_lore: list[RetrievedLore]
    state_summary: dict[str, Any]
    used_mock_llm: bool
