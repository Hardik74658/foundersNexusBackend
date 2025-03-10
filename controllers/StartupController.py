from config.database import startups_collection
from models.StartupModel import Startup,StartupOut
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse

async def getAllStartups():
    startups = await startups_collection.find().to_list
    return [StartupOut(**startup) for startup in startups]

async def getStartupById(startupId: str):
    startup = await startups_collection.find_one({"_id": ObjectId(startupId)})
    if startup is None:
        raise HTTPException(status_code=404, detail="Startup not found")
    return StartupOut(**startup)

async def addStartup(startup):
    createStartup = await startups_collection.insert_one(startup.dict(exclude_unset=True))
    startupId = str(createStartup.inserted_id)
    return JSONResponse({
        "message": "Startup created successfully",
        "startupId": str(startupId)
    },status_code=201)

async def deleteStartup(startupId: str):
    deleteStartup = await startups_collection.delete_one({"_id": ObjectId(startupId)})  
    if deleteStartup.deleted_count == 1:
        return JSONResponse({
            "message": "Startup deleted successfully"
        })
    raise HTTPException(status_code=404, detail="Startup not found")