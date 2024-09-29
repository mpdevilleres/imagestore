import uuid


async def test_create_frames(
    settings, http_client, mongo_client, minio_client, image_csv
):
    filename = f"{uuid.uuid4().hex}.csv"
    files = {"file": (filename, open(image_csv, "rb"))}
    response = http_client.post("/frames", files=files)

    assert response.status_code == 201

    # checks if the file is getting uploaded to s3/minio
    response = minio_client.get_object(settings.MINIO_BUCKET_NAME, filename)
    assert response.data

    # checks if the frames are inserted in database
    collection = mongo_client[settings.MONGO_DATABASE][settings.MONGO_COLLECTION]
    cursor = collection.find({})
    frames = await cursor.to_list()
    assert len(frames) == 200

    # check if the document has the expected schema
    frame = frames[0]
    expected_keys = {"depth", *[f"col{i}" for i in range(1, 151)]}
    assert expected_keys <= frame.keys()
    assert len(frame.keys()) == 152  # 152 because there's a _id field added by mongodb


async def test_retrieve_frames_invalid_filters(http_client):
    response = http_client.get(
        "/frames",
        params={"depth_min": 3, "depth_max": 2},
    )

    assert response.status_code == 422


async def test_retrieve_frames_no_filters(http_client):
    response = http_client.get(
        "/frames",
    )

    assert response.status_code == 422


def test_retrieve_frames_valid(http_client, frames):
    response = http_client.get(
        "/frames",
        params={
            "depth_min": 9000,
            "depth_max": 9500,
            "colormap": "inferno",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["image_base64"]
