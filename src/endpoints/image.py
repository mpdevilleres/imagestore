from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Depends, status, HTTPException, Query
from fastapi.responses import HTMLResponse
from minio import Minio
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import Settings
from src.dependency import get_minio_provider, get_mongo_provider, get_settings_provider
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

    image_base64 = await image_repository.retrieve_base64_rendered_frames(filters=filters)
    return {
        'image_base64': image_base64
    }


@router.get("/show-frames", response_class=HTMLResponse)
async def show_frames():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Image Renderer</title>
        <style>
            /* Basic styling for the form and image */
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
    
            form {
                margin-bottom: 20px;
            }
    
            label {
                margin-right: 10px;
            }
    
            input, select {
                margin-right: 20px;
            }
    
            #image-container {
                margin-top: 20px;
                display: none; /* Hide the image container initially */
                background-color: white; /* Ensure background is opaque */
            }
    
            #rendered-image {
                max-width: 100%;
                height: auto;
                display: none; /* Hide the image until it's fully loaded */
            }
        </style>
    </head>
    <body>
    
    <h1>Render Image from API</h1>
    
    <form id="image-form">
        <label for="depth_min">Depth Min:</label>
        <input type="number" id="depth_min" name="depth_min" required>
    
        <label for="depth_max">Depth Max:</label>
        <input type="number" id="depth_max" name="depth_max" required>
    
        <label for="colormap">Colormap:</label>
        <select id="colormap" name="colormap">
            <option value="viridis">viridis</option>
            <option value="plasma">plasma</option>
            <option value="inferno">inferno</option>
            <option value="magma">magma</option>
        </select>
    
        <button type="submit">Submit</button>
    </form>
    
    <div id="image-container">
        <img id="rendered-image" src="" alt="Rendered Image">
    </div>
    
    <script>
        // Handle form submission
        document.getElementById('image-form').addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent the default form submission
    
            // Get the image element and image container
            const imgElement = document.getElementById('rendered-image');
            const imageContainer = document.getElementById('image-container');
    
            // Hide the image container and image during the fetch request
            imageContainer.style.display = 'none';
            imgElement.style.display = 'none';
    
            // Clear the previous image's src
            imgElement.src = '';
    
            // Get form values
            const depthMin = document.getElementById('depth_min').value;
            const depthMax = document.getElementById('depth_max').value;
            const colormap = document.getElementById('colormap').value;
    
            // Build the query string
            const queryParams = new URLSearchParams({
                depth_min: depthMin,
                depth_max: depthMax,
                colormap: colormap
            });
    
            // Fetch the image from the API
            fetch(`/frames?${queryParams.toString()}`)
                .then(response => response.json())
                .then(data => {
                    if (data.image_base64) {
                        // Set the image source to the base64 data
                        imgElement.src = `data:image/png;base64,${data.image_base64}`;
    
                        // Show the image container when the image has fully loaded
                        imgElement.onload = function () {
                            imageContainer.style.display = 'block';
                            imgElement.style.display = 'block';
                        };
                    } else {
                        alert('No image data received.');
                    }
                })
                .catch(error => {
                    console.error('Error fetching the image:', error);
                    alert('An error occurred while fetching the image.');
                });
        });
    </script>
    
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
