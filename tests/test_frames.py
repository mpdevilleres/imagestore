import uuid



async def test_create_frames(settings, http_client, mongo_client, minio_client, image_csv):
    filename = f"{uuid.uuid4().hex}.csv"
    files = {"file": (filename, open(image_csv, "rb"))}
    response = http_client.post("/api/v1/frames", files=files)

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
    expected_keys = {'depth', *[f'col{i}' for i in range(1, 151)]}
    assert expected_keys <= frame.keys()
    assert len(frame.keys()) == 152  # 152 because there's a _id field added by mongodb


async def test_retrieve_frames_invalid_filters(http_client):
    response = http_client.get(
        "/api/v1/frames",
        params={"depth_min": 3, 'depth_max': 2},
    )

    assert response.status_code == 422


async def test_retrieve_frames_no_filters(http_client):
    response = http_client.get(
        "/api/v1/frames",
    )

    assert response.status_code == 422
