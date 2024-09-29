# in this codebase we try to not have hardcoded names for the columns as to have guarantee
# that we follow the original data format and specification
# we also depend on types to improve readability and avoid runtime value/type errors
import asyncio
from pathlib import Path

import polars as pl
import numpy as np
from scipy.ndimage import zoom
from loguru import logger
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorCollection

BASE_DIR = Path(__file__).resolve().parent
IMAGE_CSV_PATH = BASE_DIR / 'data' / 'img.csv'


def get_mongo_db_client(db_name, collection_name) -> AsyncIOMotorCollection:
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://root:example@localhost:27017/?authSource=admin"
    )
    return client[db_name][collection_name]


def resize_row(row: dict, depth_name: str, column_names: list[str], new_width: int):
    data = [value for key, value in row.items() if key != depth_name]

    logger.debug(f'resizing a frame from {len(data)} to {new_width}')

    pixels = np.array(data, dtype=float)
    zoom_factor = new_width / len(data)
    resized_row: np.ndarray = zoom(pixels, zoom_factor)

    logger.debug(f'resizing successful image is now {resized_row.size} pixels')

    result = dict(zip(column_names[:new_width], resized_row))
    result[depth_name] = row[depth_name]
    return result


def insert_row_to_mongo(filename, database, collection, df):
    mongo_collection: AsyncIOMotorCollection = get_mongo_db_client(database, collection)
    documents = []

    for row in df.rows(named=True):
        documents.append(
            {
                filename: filename,
                'depth': row['depth'],
                'pixels': [value for key, value in row.items() if key != 'depth'],
            }
        )

    mongo_collection.insert_many(documents)


async def main():
    df: pl.DataFrame = pl.read_csv(IMAGE_CSV_PATH)
    column_names: list[str] = df.columns[1:]
    depth_name: str = df.columns[0]
    new_width: int = 150

    resized_rows = [resize_row(row, depth_name, column_names, new_width) for row in df.rows(named=True)]

    resized_df = pl.DataFrame(resized_rows)

    print(resized_df.shape)
    insert_row_to_mongo(filename='1.csv', database='image', collection='frames', df=resized_df)


if __name__ == '__main__':
    asyncio.run(main())
