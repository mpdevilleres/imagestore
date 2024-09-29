from fastapi import APIRouter, UploadFile, File, Depends, status
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import Settings
from src.dependency import get_minio_provider, get_mongo_provider, get_settings_provider
from src.repository import ImageRepository

router = APIRouter()

DEFAULT_TAG = "Image"


@router.post(
    "/image/upload",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_201_CREATED,
)
async def image_upload(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings_provider()),
    minio_client: Minio = Depends(get_minio_provider()),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_provider()),
):
    image_repository = ImageRepository(
        mongo_client=mongo_client,
        minio_client=minio_client,
        settings=settings,
    )

    # try:
    await image_repository.process(file)

    # except Exception as e:
    #     # for now, we will raise all errors for simplicity,
    #     # but it is ideal to handle errors based on the expection
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
