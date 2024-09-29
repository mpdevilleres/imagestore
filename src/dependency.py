from typing import Callable
from fastapi import Request, Depends
from minio import Minio

from src.config import Settings, get_settings
from src.datastore import get_minio_client, get_mongo_client


def get_settings_provider(*, runtime=None, new=False) -> Callable:
    def _provider(request: Request) -> Settings:
        settings = get_settings(runtime=runtime or request, new=new)
        yield settings

    return _provider


def get_minio_provider(*, runtime=None, new=False) -> Callable:
    def _provider(
        request: Request,
        settings: Settings = Depends(get_settings_provider()),
    ) -> Minio:
        client = get_minio_client(settings, runtime=runtime or request, new=new)
        yield client

    return _provider


def get_mongo_provider(*, runtime=None, new=False) -> Callable:
    def _provider(
        request: Request,
        settings: Settings = Depends(get_settings_provider()),
    ) -> Minio:
        client = get_mongo_client(settings, runtime=runtime or request, new=new)
        yield client

    return _provider
