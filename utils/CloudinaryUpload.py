import cloudinary
import cloudinary.uploader
import io
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)



async def upload_image_from_buffer(file):
    contents = await file.read()
    buffer = io.BytesIO(contents)
    buffer.name = file.filename
    response = cloudinary.uploader.upload(buffer)
    return response["secure_url"]