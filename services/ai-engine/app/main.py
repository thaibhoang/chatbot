from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Omni-RAG AI Engine", version="0.1.0")
    app.state.settings = settings
    app.include_router(api_router, prefix="/v1")
    return app


app = create_app()
