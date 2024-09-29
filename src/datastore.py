from urllib.parse import urlparse

from fastapi import FastAPI
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import Settings


def get_minio_client(settings: Settings, *, runtime: FastAPI = None, new=True) -> Minio:
    """
    :param settings: Application settings
    :param runtime: the object that is currently running in the process this can be FastAPI or ARQ
    :param new: flag to indicate to create a new runtime or reuse the attached runtime
    """

    if new:
        endpoint = urlparse(settings.MINIO_ENDPOINT_URL)
        secure = endpoint.scheme == "https"

        client = Minio(
            endpoint=endpoint.netloc,
            access_key=settings.MINIO_ACCESS_KEY_ID,
            secret_key=settings.MINIO_SECRET_ACCESS_KEY,
            region=settings.MINIO_REGION,
            secure=secure,
        )

        return client

    if isinstance(runtime, FastAPI):
        return runtime.minio_client
    return runtime.app.minio_client


def get_mongo_client(
    settings: Settings, *, runtime: FastAPI = None, new=True
) -> AsyncIOMotorClient:
    """
    :param settings: Application settings
    :param runtime: the object that is currently running in the process this can be FastAPI or ARQ
    :param new: flag to indicate to create a new runtime or reuse the attached runtime
    """

    if new:
        client = AsyncIOMotorClient(
            settings.MONGO_ENDPOINT_URL,
        )

        return client

    if isinstance(runtime, FastAPI):
        return runtime.mongo_client
    return runtime.app.mongo_client
