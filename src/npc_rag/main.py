from fastapi import FastAPI

from npc_rag.api.routes import router
from npc_rag.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local-only RAG NPC dialogue backend for games.",
)
app.include_router(router, prefix="/api/v1")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}
