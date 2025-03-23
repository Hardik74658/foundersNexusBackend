from fastapi import APIRouter
from models.StartupModel import Startup
from controllers import StartupController


router = APIRouter()

@router.get("/startups/",tags=["Startups"])
async def get_all_startups():
    return await StartupController.getAllStartups()

@router.post("/startups/",tags=["Startups"])
async def add_startup(startup: Startup):
    return await StartupController.addStartup(startup)

@router.get("/startups/{startupId}",tags=["Startups"])
async def get_startup_by_id(startupId: str):
    return await StartupController.getStartupById(startupId)


@router.delete("/startups/{startupId}",tags=["Startups"])
async def delete_startup_by_id(startupId: str):
    return await StartupController.deleteStartup(startupId)