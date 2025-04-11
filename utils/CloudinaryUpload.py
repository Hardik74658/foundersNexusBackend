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
    # print("came to cloudinary")
    buffer.name = file.filename
    try:
        response = cloudinary.uploader.upload(buffer)
        # Log the response for debugging
        print(f"Cloudinary upload response: {response}")
        secure_url = response.get("secure_url")
        if not secure_url:
            print("Error: 'secure_url' not found in Cloudinary response.")
            return ""
        return secure_url
    except Exception as e:
        # Log the error for debugging
        print(f"Error uploading to Cloudinary: {e}")
        return ""