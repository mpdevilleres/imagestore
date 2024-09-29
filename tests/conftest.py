import uuid
import csv
import random

import pytest

from fastapi.testclient import TestClient
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import Settings
from src.datastore import get_minio_client, get_mongo_client
from src.factory import create_app


@pytest.fixture
def settings() -> Settings:
    _settings = Settings()
    yield _settings


@pytest.fixture
def http_client(settings):
    _app = create_app(settings)
    with TestClient(_app) as _client:
        yield _client


@pytest.fixture
def minio_client(settings) -> Minio:
    client = get_minio_client(settings=settings, new=True)
    yield client


@pytest.fixture
def mongo_client(settings) -> AsyncIOMotorClient:
    client = get_mongo_client(settings=settings, new=True)
    yield client


@pytest.fixture
def image_csv(tmp_path):
    file_path = tmp_path.joinpath(f"{uuid.uuid4().hex}.csv")
    headers = [
        "depth",
        *[f"col{i}" for i in range(1, 201)],
    ]  # create header with 200 columns
    rows = []

    for _ in range(200):
        pixels = [random.randrange(0, 255) for _ in range(200)]
        rows.append([random.uniform(9000, 9550), *pixels])
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(rows)

    yield file_path


@pytest.fixture
async def frames(settings, mongo_client):
    collection = mongo_client[settings.MONGO_DATABASE][settings.MONGO_COLLECTION]
    rows = []
    for _ in range(200):
        pixels = {f"col{i}": random.randrange(0, 255) for i in range(200)}
        rows.append(
            {"depth": random.uniform(9000, 9550), **pixels},
        )

    await collection.insert_many(rows)

    yield
