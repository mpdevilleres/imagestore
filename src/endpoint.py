from typing import Annotated
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    status,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import Settings
from src.dependency import (
    get_minio_provider,
    get_mongo_provider,
    get_settings_provider,
    get_templates_provider,
)
from src.repository import ImageRepository
from src.schema import ImageFilterParams

router = APIRouter()

DEFAULT_TAG = "Image"


@router.post(
    "/frames",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_201_CREATED,
)
async def create_frames(
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

    try:
        await image_repository.process(file)

    except Exception as e:
        # for now, we will raise all errors for simplicity,
        # but it is ideal to handle errors based on the expection
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/frames",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_200_OK,
)
async def retrieve_frames(
    filters: Annotated[ImageFilterParams, Query()],
    settings: Settings = Depends(get_settings_provider()),
    minio_client: Minio = Depends(get_minio_provider()),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_provider()),
):
    image_repository = ImageRepository(
        mongo_client=mongo_client,
        minio_client=minio_client,
        settings=settings,
    )

    image_base64 = await image_repository.retrieve_base64_rendered_frames(
        filters=filters
    )
    return {"image_base64": image_base64}


@router.get("/show-frames", response_class=HTMLResponse)
async def show_frames(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates_provider()),
):
    return templates.TemplateResponse(request, "index.jinja2")
