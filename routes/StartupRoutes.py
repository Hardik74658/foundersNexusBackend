from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models.StartupModel import Startup
from controllers.StartupController import addStartup, getAllStartups, getStartupById, deleteStartup
import json

router = APIRouter()

@router.get("/startups/", tags=["Startups"])
async def get_all_startups():
    return await getAllStartups()

@router.post("/startups/", tags=["Startups"])
async def create_startup_with_file(
    startup_name: str = Form(...),
    description: str = Form(...),
    industry: str = Form(...),
    website: str = Form(None),
    market_size: str = Form(...),
    revenue_model: str = Form(None),
    founders: str = Form(...),  # JSON string of founder IDs
    previous_fundings: str = Form(None),  # JSON string of funding details
    equity_split: str = Form(None),  # JSON string of equity split details
    logo: UploadFile = File(None)
):
    try:
        # Parse JSON strings into Python objects
        founders_list = json.loads(founders)  # List of founder IDs
        previous_fundings_list = json.loads(previous_fundings) if previous_fundings else []  # List of funding objects
        equity_split_list = json.loads(equity_split) if equity_split else []  # List of equity split objects

        # Create a dictionary for the startup data
        startup_data = {
            "startup_name": startup_name,
            "description": description,
            "industry": industry,
            "website": website,
            "market_size": market_size,
            "revenue_model": revenue_model,
            "founders": founders_list,
            "previous_fundings": previous_fundings_list,
            "equity_split": equity_split_list,
        }

        # Validate and process the startup data
        return await addStartup(Startup(**startup_data), logo)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating startup: {str(e)}")

@router.get("/startups/{startupId}", tags=["Startups"])
async def get_startup_by_id(startupId: str):
    return await getStartupById(startupId)

@router.delete("/startups/{startupId}", tags=["Startups"])
async def delete_startup_by_id(startupId: str):
    return await deleteStartup(startupId)