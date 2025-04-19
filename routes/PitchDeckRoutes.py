import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, Query, Path
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder  # new import
from typing import Optional, List
from datetime import date
import json
from models.PitchDeckModel import PitchDeckOut, PitchDeckCreate, PitchDeckUpdate
from controllers.PitchDeckController import (
    upload_pitch_deck, get_all_pitch_decks, get_pitch_deck_by_id,
    update_pitch_deck, delete_pitch_deck, set_pitch_deck_active, get_active_pitch_deck
)
  
router = APIRouter()
logger = logging.getLogger("pitchdeck")

@router.post("/pitchdecks/", tags=["Pitch Decks"])
async def create_pitch_deck(
    title: str = Form(...),
    startupId: str = Form(..., alias="startup_id"),   # accept startup_id from form
    description: Optional[str] = Form(None),
    raise_until: Optional[str] = Form(None),
    target_amount: Optional[str] = Form(None),
    round: Optional[str] = Form(None),
    external_link: Optional[str] = Form(None),
    active: bool = Form(False),
    file: UploadFile = File(...)
):
    """
    Upload a new pitch deck file (PDF/PPT/PPTX) with metadata.
    
    - **title**: Title of the pitch deck
    - **startupId**: ID of the startup this deck belongs to
    - **description**: Optional description
    - **file**: PDF or PowerPoint file (max 50MB)
    - **raise_until**: Optional date until which funding is being raised (YYYY-MM-DD)
    - **target_amount**: Optional target amount to raise
    - **round**: Optional funding round (e.g., "Pre-Seed", "Seed", "Series A")
    - **external_link**: Optional external link to the pitch deck
    - **active**: Whether this pitch deck should be set as active
    """
    try:
        # Parse raise_until if provided
        raise_until_date = None
        if raise_until:
            try:
                raise_until_date = date.fromisoformat(raise_until)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format for raise_until. Use YYYY-MM-DD")
        
        # Prepare deck data
        deck_data = {
            "title": title,
            "startupId": startupId,
            "description": description,
            "raise_until": raise_until_date,
            "target_amount": target_amount,
            "round": round,
            "external_link": external_link,
            "active": active
        }
        
        # Upload file and create pitch deck
        created_deck = await upload_pitch_deck(file, deck_data)
        
        # encode datetime, ObjectId etc. to JSON-friendly types
        payload = jsonable_encoder({"message": "Pitch deck uploaded successfully", "deck": created_deck})
        return JSONResponse(content=payload, status_code=201)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"create_pitch_deck error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# alias POST /pitchdeck/ → create_pitch_deck
router.post("/pitchdeck/", tags=["Pitch Decks"])(create_pitch_deck)

@router.get("/pitchdecks/", response_model=List[PitchDeckOut], tags=["Pitch Decks"])
async def get_pitch_decks(
    startupId: Optional[str] = Query(None, description="Filter by startup ID")
):
    """
    Get all pitch decks, optionally filtered by startup ID.
    """
    try:
        pitch_decks = await get_all_pitch_decks(startupId)
        return pitch_decks
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pitch decks: {str(e)}")

# alias GET /pitchdeck/ → get_pitch_decks
router.get("/pitchdeck/", response_model=List[PitchDeckOut], tags=["Pitch Decks"])(get_pitch_decks)

# new GET /pitchdeck/startup/{startupId} → filter by startup
@router.get("/pitchdeck/startup/{startupId}", response_model=List[PitchDeckOut], tags=["Pitch Decks"])
async def get_pitch_decks_by_startup(startupId: str = Path(..., description="Filter by startup ID")):
    return await get_all_pitch_decks(startupId)

@router.get("/pitchdecks/{deck_id}", response_model=PitchDeckOut, tags=["Pitch Decks"])
async def get_pitch_deck(
    deck_id: str = Path(..., description="The ID of the pitch deck to retrieve")
):
    """
    Get details of a specific pitch deck by ID.
    """
    return await get_pitch_deck_by_id(deck_id)

@router.patch("/pitchdecks/{deck_id}", response_model=PitchDeckOut, tags=["Pitch Decks"])
async def update_pitch_deck_metadata(
    deck_id: str,
    update_data: PitchDeckUpdate
):
    """
    Update metadata for an existing pitch deck.
    """
    return await update_pitch_deck(deck_id, update_data.dict(exclude_unset=True))

@router.delete("/pitchdecks/{deck_id}", tags=["Pitch Decks"])
async def remove_pitch_deck(
    deck_id: str = Path(..., description="The ID of the pitch deck to delete")
):
    """
    Delete a pitch deck by ID.
    """
    return await delete_pitch_deck(deck_id)

@router.put("/pitchdecks/{deck_id}/activate", tags=["Pitch Decks"])
async def activate_pitch_deck(
    deck_id: str = Path(..., description="The ID of the pitch deck to set as active")
):
    """
    Set a pitch deck as active and deactivate all others for the same startup.
    """
    return await set_pitch_deck_active(deck_id)

@router.get("/pitchdecks/active/{startupId}", response_model=PitchDeckOut, tags=["Pitch Decks"])
async def get_active_deck(
    startupId: str = Path(..., description="The startup ID to get the active pitch deck for")
):
    """
    Get the currently active pitch deck for a specific startup.
    """
    return await get_active_pitch_deck(startupId)
