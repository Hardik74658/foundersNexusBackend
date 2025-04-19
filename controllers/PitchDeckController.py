import os
import io
import logging
from typing import List, Optional, Dict, Any
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import datetime
from config.database import pitchdecks_collection, startups_collection, users_collection
from models.PitchDeckModel import PitchDeck, PitchDeckOut, PitchDeckUpdate
from utils.CloudinaryUpload import upload_image_from_buffer

# Set up logger first before using it anywhere
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("pitchdeck.ctrl")

# Helper function to convert ObjectId to string recursively
def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data

def generate_thumbnail_url(file_url: str, file_extension: str) -> str:
    """
    Generate a thumbnail URL by modifying the Cloudinary file URL
    to use Cloudinary's built-in PDF/PPT to image conversion
    """
    if not file_url:
        return None
    
    # Extract the file extension 
    if file_extension.lower() in ['.pdf', '.ppt', '.pptx']:
        # PPT files will be converted to PDF using Aspose, so handle accordingly
        
        # For PPT files that were converted to PDF using Aspose
        if file_extension.lower() in ['.ppt', '.pptx'] and '/raw/upload/' in file_url:
            # The file is now a PDF, construct URL for the first page as JPG
            # Change from /raw/upload/ to /image/upload/ and .pdf to .jpg
            base_url = file_url.replace('/raw/upload/', '/image/upload/')
            base_url = base_url.rsplit('.', 1)[0]  # Remove extension
            # Add transformation parameters: first page, width, height
            return f"{base_url.split('/upload/')[0]}/upload/pg_1,w_400,h_300,c_fit,q_85/{base_url.split('/upload/')[1]}.jpg"
            
        # For PDFs uploaded as image resource type
        elif '/image/upload/' in file_url:
            # For files uploaded as 'image' resource type:
            base_url = file_url.rsplit('.', 1)[0]
            # Insert transformation parameters for PDF first page
            upload_index = base_url.find('/upload/')
            if upload_index != -1:
                version_part_index = base_url.find('/', upload_index + 8)
                if version_part_index != -1:
                    thumbnail_url = (
                        f"{base_url[:upload_index+8]}"
                        f"pg_1,w_400,h_300,c_fit,q_85/"
                        f"{base_url[upload_index+8:]}.jpg"
                    )
                    return thumbnail_url
            return f"{base_url}.jpg"
    
    # For other file types, just return the original URL
    return file_url

async def upload_pitch_deck(file: UploadFile, deck_data: Dict[str, Any]) -> Dict[str, Any]:
    """Upload a pitch deck file to Cloudinary and create the database record"""
    try:
        if file.content_type not in ["application/pdf", "application/vnd.ms-powerpoint", 
                                   "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
            raise HTTPException(status_code=400, detail="File must be PDF or PowerPoint")
        
        # Check file size (max 50MB)
        await file.seek(0)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:  # 50MB in bytes
            raise HTTPException(status_code=400, detail="File size exceeds maximum of 50MB")
        
        # Reset file pointer
        await file.seek(0)
        
        try:
            # Upload file to Cloudinary
            file_extension = os.path.splitext(file.filename)[1].lower()
            is_ppt = file_extension.lower() in ['.ppt', '.pptx']
            
            file_url, cloudinary_response = await upload_image_from_buffer(file, return_response=True)
            if not file_url:
                raise HTTPException(status_code=500, detail="Failed to upload file to Cloudinary")
            
            logger.info(f"Pitch deck file uploaded successfully: {file_url}")
            logger.info(f"Cloudinary response: {cloudinary_response}")
            
            # Get slide count from Cloudinary response
            slide_count = 0
            if cloudinary_response:
                # For PDFs uploaded as images, Cloudinary provides page count
                if 'pages' in cloudinary_response:
                    slide_count = cloudinary_response['pages']
                    logger.info(f"Using page count from Cloudinary: {slide_count} pages")
                # For PPT files converted to PDF, we need to check differently
                elif is_ppt:
                    # Check for pages in resource response
                    if 'resource_type' in cloudinary_response and cloudinary_response['resource_type'] == 'raw':
                        # For PPT files converted to PDF, we need to make an additional API call 
                        # to get the PDF page count, but we'll set a reasonable default for now
                        slide_count = 10  # Default count - in production you'd want to get actual count
                        logger.info(f"Using estimated slide count for PPT: {slide_count}")
            
            # If we still don't have a slide count, set to default
            if slide_count == 0:
                slide_count = 1
                logger.info(f"Using default slide count: {slide_count}")
                
            # Generate a thumbnail URL
            thumbnail_url = generate_thumbnail_url(file_url, file_extension)
            if thumbnail_url:
                logger.info(f"Generated thumbnail URL: {thumbnail_url}")
            
            # For PPTs, also create a view URL that works in browser
            view_url = file_url
            if is_ppt:
                # The PPT was converted to PDF, so we can use it directly
                if file_url.endswith('.pdf'):
                    view_url = file_url
                else:
                    # Ensure we have a proper viewing URL
                    view_url = file_url + ".pdf" if not file_url.endswith('.pdf') else file_url
            
            # Prepare pitch deck document
            startup_id = ObjectId(deck_data["startupId"])
            
            # Make all other decks inactive if this one is to be active
            if deck_data.get("active", False):
                await pitchdecks_collection.update_many(
                    {"startupId": startup_id, "active": True},
                    {"$set": {"active": False}}
                )
            
            # Ensure raise_until is a datetime, not a date
            ru = deck_data.get("raise_until")
            if isinstance(ru, datetime.date) and not isinstance(ru, datetime.datetime):
                ru = datetime.datetime.combine(ru, datetime.time())
            
            pitch_deck = {
                "title": deck_data["title"],
                "description": deck_data.get("description"),
                "startupId": startup_id,
                "file_url": file_url,
                "view_url": view_url,  # URL optimized for viewing in browser
                "thumbnail_url": thumbnail_url,
                "active": deck_data.get("active", False),
                "raise_until": ru,
                "target_amount": deck_data.get("target_amount"),
                "round": deck_data.get("round"),
                "slides_count": slide_count,
                "file_type": file_extension,
                "external_link": deck_data.get("external_link"),
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
            
            # Insert into database
            result = await pitchdecks_collection.insert_one(pitch_deck)
            deck_id = result.inserted_id
            
            if not deck_id:
                raise HTTPException(status_code=500, detail="Failed to create pitch deck")
            
            # Get the full deck data with startup details
            created_deck = await pitchdecks_collection.find_one({"_id": deck_id})
            
            return convert_objectid_to_str(created_deck)
        except Exception as e:
            logger.error(f"Error in processing or uploading file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Error processing file") from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"upload_pitch_deck failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process pitch deck")

async def get_all_pitch_decks(startupId: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all pitch decks, optionally filtered by startupId"""
    query = {}
    if startupId:
        query["startupId"] = ObjectId(startupId)
    
    pitch_decks = await pitchdecks_collection.find(query).to_list(length=None)
    
    # Enhance with startup data
    for i, deck in enumerate(pitch_decks):
        if "startupId" in deck:
            startup = await startups_collection.find_one({"_id": deck["startupId"]})
            if startup:
                pitch_decks[i]["startup"] = startup
    
    # Convert ObjectIds to strings
    return [convert_objectid_to_str(deck) for deck in pitch_decks]

async def get_pitch_deck_by_id(deck_id: str) -> Dict[str, Any]:
    """Get a specific pitch deck by ID"""
    try:
        deck = await pitchdecks_collection.find_one({"_id": ObjectId(deck_id)})
        if not deck:
            raise HTTPException(status_code=404, detail="Pitch deck not found")
        
        # Get startup data
        if "startupId" in deck:
            startup = await startups_collection.find_one({"_id": deck["startupId"]})
            if startup:
                deck["startup"] = startup
        
        return convert_objectid_to_str(deck)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid pitch deck ID")

async def update_pitch_deck(deck_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a pitch deck's metadata"""
    try:
        # First, validate that the deck exists
        deck = await pitchdecks_collection.find_one({"_id": ObjectId(deck_id)})
        if not deck:
            raise HTTPException(status_code=404, detail="Pitch deck not found")
        
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.datetime.now()
        
        # Update the deck
        result = await pitchdecks_collection.update_one(
            {"_id": ObjectId(deck_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return JSONResponse(
                content={"message": "No changes made to pitch deck"},
                status_code=200
            )
        
        # Get and return updated deck
        updated_deck = await pitchdecks_collection.find_one({"_id": ObjectId(deck_id)})
        
        # Get startup data
        if "startupId" in updated_deck:
            startup = await startups_collection.find_one({"_id": updated_deck["startupId"]})
            if startup:
                updated_deck["startup"] = startup
        
        return convert_objectid_to_str(updated_deck)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid pitch deck ID")

async def delete_pitch_deck(deck_id: str) -> Dict[str, Any]:
    """Delete a pitch deck"""
    try:
        deck = await pitchdecks_collection.find_one({"_id": ObjectId(deck_id)})
        if not deck:
            raise HTTPException(status_code=404, detail="Pitch deck not found")
        
        result = await pitchdecks_collection.delete_one({"_id": ObjectId(deck_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete pitch deck")
        
        # Note: In a production environment, you might want to also delete the file from Cloudinary
        
        return {"message": "Pitch deck deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid pitch deck ID")

async def set_pitch_deck_active(deck_id: str) -> Dict[str, Any]:
    """Set a pitch deck as active and deactivate all others for that startup"""
    try:
        # Validate deck exists
        deck = await pitchdecks_collection.find_one({"_id": ObjectId(deck_id)})
        if not deck:
            raise HTTPException(status_code=404, detail="Pitch deck not found")
        
        # Deactivate all decks for this startup
        await pitchdecks_collection.update_many(
            {"startupId": deck["startupId"]},
            {"$set": {"active": False}}
        )
        
        # Activate the selected deck
        result = await pitchdecks_collection.update_one(
            {"_id": ObjectId(deck_id)},
            {"$set": {"active": True, "updated_at": datetime.datetime.now()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to activate pitch deck")
        
        return {"message": "Pitch deck set as active successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid pitch deck ID")

async def get_active_pitch_deck(startupId: str) -> Dict[str, Any]:
    """Get the active pitch deck for a startup"""
    try:
        deck = await pitchdecks_collection.find_one({
            "startupId": ObjectId(startupId),
            "active": True
        })
        
        if not deck:
            raise HTTPException(status_code=404, detail="No active pitch deck found")
        
        # Get startup data
        if "startupId" in deck:
            startup = await startups_collection.find_one({"_id": deck["startupId"]})
            if startup:
                deck["startup"] = startup
        
        return convert_objectid_to_str(deck)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid startup ID")
