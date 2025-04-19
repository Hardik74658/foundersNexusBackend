import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import os
import logging
import tempfile
from typing import Dict, Any, Tuple, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

logger = logging.getLogger("cloudinary.upload")

async def upload_image_from_buffer(file: UploadFile, return_response: bool = False) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Upload file to Cloudinary from a buffer
    For PPT files, uses appropriate resource type and options for best handling
    Returns the URL of the uploaded file and optionally the full response
    """
    temp_file_path = None
    try:
        # Read file content
        contents = await file.read()
        if not contents:
            logger.error("File is empty")
            return None, None

        # Determine file extension and proper resource type
        filename = file.filename
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Default upload parameters
        upload_params = {
            "folder": "pitch_decks",
            "resource_type": "auto",
        }
        
        # Special handling for PowerPoint files - try different approach
        if file_extension in ['.ppt', '.pptx']:
            # Method 1: Try using image resource type for PowerPoint
            upload_params.update({
                "resource_type": "image",  # Try handling as image
                # Don't use Aspose conversion as it's causing errors
            })
        elif file_extension == '.pdf':
            # For PDFs, use image resource type for better thumbnail support
            upload_params["resource_type"] = "image"
        
        # Log the upload parameters for debugging
        logger.info(f"Uploading file {filename} with params: {upload_params}")
        
        # Create a temporary file to handle binary data properly
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name
        
        # Upload to Cloudinary using the temporary file path
        response = cloudinary.uploader.upload_large(
            temp_file_path,
            filename=filename,
            **upload_params
        )
        
        if not response or "secure_url" not in response:
            logger.error(f"Invalid response from Cloudinary: {response}")
            return None, None
            
        logger.info(f"Upload successful: {response['secure_url']}")
        
        if return_response:
            return response["secure_url"], response
        return response["secure_url"], None
        
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}", exc_info=True)
        
        # If first method fails for PowerPoint, try alternate method
        if file_extension in ['.ppt', '.pptx'] and "resource_type" in upload_params and upload_params["resource_type"] == "image":
            try:
                logger.info(f"First PowerPoint upload method failed, trying alternate method")
                # Method 2: Use raw resource type without Aspose
                upload_params.update({
                    "resource_type": "raw",  # Try as raw
                })
                
                # Create a new temporary file since the previous one might be closed
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    await file.seek(0)  # Rewind the file
                    contents = await file.read()
                    temp_file.write(contents)
                    temp_file_path = temp_file.name
                
                # Try uploading again with new params
                response = cloudinary.uploader.upload_large(
                    temp_file_path,
                    filename=filename,
                    **upload_params
                )
                
                if response and "secure_url" in response:
                    logger.info(f"Alternate upload method successful: {response['secure_url']}")
                    if return_response:
                        return response["secure_url"], response
                    return response["secure_url"], None
                else:
                    logger.error(f"Alternate upload method failed: {response}")
            except Exception as e2:
                logger.error(f"Error in alternate upload method: {str(e2)}", exc_info=True)
        
        return None, None
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.error(f"Error deleting temporary file: {str(e)}")