import uuid


async def test_upload(settings, http_client, mongo_client, minio_client, image_csv):
    filename = f"{uuid.uuid4().hex}.csv"
    files = {"file": (filename, open(image_csv, "rb"))}
    response = http_client.post("/api/v1/image/upload", files=files)

    assert response.status_code == 201

    # checks if the file is getting uploaded to s3/minio
    response = minio_client.get_object(settings.MINIO_BUCKET_NAME, filename)
    assert response.data

    # checks if the frames are inserted in database
    collection = mongo_client[settings.MONGO_DATABASE][settings.MONGO_COLLECTION]
    cursor = collection.find({"filename": filename})
    frames = await cursor.to_list()
    assert len(frames) == 200

    # check if the document has the expected schema
    frame = frames[0]
    assert {"filename", "depth", "pixels"} <= frame.keys()
    assert len(frame["pixels"]) == 150
