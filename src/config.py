from pathlib import Path

from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Metadata
    # ========================================================
    PROJECT_NAME: str = "Image Store"
    BUILD_TAG: str
    BUILD_COMMIT: str
    BASE_DIR: Path = Path(__file__).parent.parent
    SOURCE_DIR: Path = BASE_DIR.joinpath("src")
    TEMPLATES_DIR: Path = BASE_DIR.joinpath("templates")

    # System Dependencies
    # ========================================================
    MINIO_ACCESS_KEY_ID: str
    MINIO_SECRET_ACCESS_KEY: str
    MINIO_REGION: str
    MINIO_BUCKET_NAME: str
    MINIO_ENDPOINT_URL: str

    MONGO_USERNAME: str
    MONGO_PASSWORD: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DATABASE: str
    MONGO_COLLECTION: str

    @property
    def MONGO_ENDPOINT_URL(self):
        return (
            f"mongodb://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}"
            f"@{self.MONGO_HOST}:{self.MONGO_PORT}"
        )


def get_settings(runtime: FastAPI = None, new=False) -> Settings:
    if new:
        return Settings()

    if isinstance(runtime, FastAPI):
        return runtime.settings
    return runtime.app.settings
