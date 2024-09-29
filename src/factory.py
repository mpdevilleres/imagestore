from typing import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.datastore import get_minio_client, get_mongo_client
from src.endpoints.image import router as image_router
from src.config import Settings, get_settings


def lifespan_provider(settings: Settings) -> Callable:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.minio_client = get_minio_client(settings=settings, new=True)
        app.mongo_client = get_mongo_client(settings=settings, new=True)
        yield

    return lifespan


def create_app(settings: Settings = None) -> FastAPI:
    settings = settings or get_settings(new=True)
    lifespan = lifespan_provider(settings)

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=f"{settings.BUILD_TAG}-{settings.BUILD_COMMIT}",
        lifespan=lifespan,
    )

    # attached the settings to the app so it is accessible to the entire process
    # without requiring to re-instantiating settings
    app.settings = settings

    # Endpoints
    app.include_router(prefix="/api/v1", router=image_router)

    return app
