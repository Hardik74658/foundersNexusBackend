from fastapi import APIRouter
from models.StartupModel import Startup
from controllers import StartupController


router = APIRouter()

@router.get("/startups/")
async def get_all_startups():
    return await StartupController.getAllStartups()

@router.post("/startups/")
async def add_startup(startup: Startup):
    return await StartupController.addStartup(startup)

@router.get("/startups/{startupId}")
async def get_startup_by_id(startupId: str):
    return await StartupController.getStartupById(startupId)