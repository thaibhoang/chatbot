from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.settings import get_settings
from app.services.memory.service import get_memory_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    memory = get_memory_service()
    await memory.startup()
    try:
        yield
    finally:
        await memory.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Omni-RAG AI Engine", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.include_router(api_router, prefix="/v1")
    return app


app = create_app()
