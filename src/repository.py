import base64
from io import BytesIO

import polars as pl
import numpy as np
from scipy.ndimage import zoom
import matplotlib.pyplot as plt
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from src.config import Settings
from src.schema import ImageFilterParams, ColorMap


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

    def get_image_collection(self):
        return self.mongo_client[self.settings.MONGO_DATABASE][
            self.settings.MONGO_COLLECTION
        ]

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

    async def create_frames(self, rows):
        collection = self.get_image_collection()
        await collection.insert_many(rows)

    async def delete_all_frames(self):
        collection = self.get_image_collection()
        await collection.delete_many({})

    async def retrieve_frames(self, filters: ImageFilterParams):
        collection = self.get_image_collection()
        cursor = collection.find(
            {"depth": {"$gte": filters.depth_min, "$lte": filters.depth_max}},
            {"_id": False},
        )
        frames = await cursor.to_list()
        return frames

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

        # as this is only intended to be serve a single file we need to delete everything before inserting new frames
        await self.delete_all_frames()
        await self.create_frames(resized_rows)

    @staticmethod
    def render_frames(frames, colormap: ColorMap):
        df = pl.DataFrame(frames)
        logger.debug(f"dataframe shape {df.shape}")
        df = df.sort("depth")
        columns = [f"col{i}" for i in range(1, 151)]

        depth_values = df["depth"].to_numpy()
        column_values = df[columns].to_numpy()

        depth_values = depth_values.flatten()

        # Compute depth edges
        if len(depth_values) == 1:
            depth_edges = np.array([depth_values[0] - 0.5, depth_values[0] + 0.5])
        elif len(depth_values) == 2:
            depth_edges = np.zeros(3)
            depth_edges[1] = (depth_values[0] + depth_values[1]) / 2
            depth_edges[0] = depth_values[0] - (depth_edges[1] - depth_values[0])
            depth_edges[2] = depth_values[1] + (depth_values[1] - depth_edges[1])
        else:
            depth_edges = np.zeros(len(depth_values) + 1)
            depth_edges[1:-1] = (depth_values[:-1] + depth_values[1:]) / 2
            depth_edges[0] = depth_values[0] - (depth_values[1] - depth_values[0]) / 2
            depth_edges[-1] = (
                depth_values[-1] + (depth_values[-1] - depth_values[-2]) / 2
            )

        x_edges = np.arange(0.5, 150.5 + 1)
        plt.pcolormesh(
            x_edges, depth_edges, column_values, cmap=colormap.value, shading="flat"
        )
        plt.xlabel("Pixel")
        plt.ylabel("Depth")
        plt.colorbar(label="Intensity")
        # this is to invert the depth
        # plt.gca().invert_yaxis()
        # plt.show()

        buffer = BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0)
        plt.close()
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return img_base64

    async def retrieve_base64_rendered_frames(self, filters: ImageFilterParams):
        frames = await self.retrieve_frames(filters)
        return self.render_frames(frames, filters.colormap)
