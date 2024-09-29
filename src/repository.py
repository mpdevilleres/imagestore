from io import BytesIO
import polars as pl
import numpy as np
from scipy.ndimage import zoom

from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from src.config import Settings


class ImageRepository:
    def __init__(
        self,
        mongo_client: AsyncIOMotorClient,
        minio_client: Minio,
        *,
        settings: Settings,
    ):
        self.mongo_client = mongo_client
        self.minio_client = minio_client
        self.settings = settings

    @staticmethod
    def _resize_row(
        row: dict, depth_name: str, column_names: list[str], new_width: int
    ):
        data = [value for key, value in row.items() if key != depth_name]

        logger.debug(f"resizing a frame from {len(data)} to {new_width}")

        pixels = np.array(data, dtype=float)
        zoom_factor = new_width / len(data)
        resized_row: np.ndarray = zoom(pixels, zoom_factor)

        logger.debug(f"resizing successful image is now {resized_row.size} pixels")

        result = {
            depth_name: row[depth_name],
            **dict(zip(column_names[:new_width], resized_row)),
        }
        return result

    def _upload_to_minio(self, buffer, filename, length):
        self.minio_client.put_object(
            bucket_name=self.settings.MINIO_BUCKET_NAME,
            object_name=filename,
            data=buffer,
            length=length,
        )

    async def _create_records(self, rows, filename):
        documents = []
        for row in rows:
            documents.append(
                {
                    "filename": filename,
                    "depth": row["depth"],
                    "pixels": [value for key, value in row.items() if key != "depth"],
                }
            )

        collection = self.mongo_client[self.settings.MONGO_DATABASE][
            self.settings.MONGO_COLLECTION
        ]
        await collection.insert_many(documents)

    async def process(self, file):
        content = file.file.read()
        buffer = BytesIO(content)
        buffer.seek(0, 2)
        length = buffer.tell()
        buffer.seek(0)

        # we back up the file for future reference
        self._upload_to_minio(buffer, file.filename, length)

        # transform data
        df: pl.DataFrame = pl.read_csv(content)
        column_names: list[str] = df.columns[1:]
        depth_name: str = df.columns[0]
        new_width: int = 150
        resized_rows = [
            self._resize_row(row, depth_name, column_names, new_width)
            for row in df.rows(named=True)
        ]
        await self._create_records(resized_rows, file.filename)
