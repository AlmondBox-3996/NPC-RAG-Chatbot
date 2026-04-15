from fastapi import APIRouter, Depends, HTTPException

from npc_rag.api.dependencies import get_dialogue_orchestrator
from npc_rag.orchestrator.dialogue_service import DialogueOrchestrator
from npc_rag.schemas.dialogue import DialogueQuery, DialogueResponse, NpcChatRequest


router = APIRouter(tags=["dialogue"])
public_router = APIRouter(tags=["npc"])


@router.post("/dialogue/query", response_model=DialogueResponse)
def query_dialogue(
    payload: DialogueQuery,
    orchestrator: DialogueOrchestrator = Depends(get_dialogue_orchestrator),
) -> DialogueResponse:
    try:
        return orchestrator.answer_with_options(
            player_id=payload.player_id,
            npc_id=payload.npc_id,
            question=payload.question,
            debug=payload.debug,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@public_router.post("/npc/chat", response_model=DialogueResponse)
def npc_chat(
    payload: NpcChatRequest,
    orchestrator: DialogueOrchestrator = Depends(get_dialogue_orchestrator),
) -> DialogueResponse:
    try:
        return orchestrator.answer_with_options(
            player_id=payload.player_id,
            npc_id=payload.npc_id,
            question=payload.message,
            debug=payload.debug,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
