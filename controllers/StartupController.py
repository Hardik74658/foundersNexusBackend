from config.database import startups_collection,users_collection
from models.StartupModel import Startup, StartupOut
from bson import ObjectId
from fastapi import HTTPException, Response, status
from fastapi.responses import JSONResponse

def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data


async def getAllStartups():
    startups = await startups_collection.find().to_list()

    for startup in startups:
        if "founders" in startup:
            for i, founder in enumerate(startup["founders"]):
                founderId = ObjectId(founder)
                founderData  = await users_collection.find_one({"_id": founderId})
                if founderData:
                    startup["founders"][i] = founderData

    
    startups = convert_objectid_to_str(startups)
    return [StartupOut(**startup) for startup in startups]

async def getStartupById(startupId: str):
    startup = await startups_collection.find_one({"_id": ObjectId(startupId)})

    if "founders" in startup:
        for i, founder in enumerate(startup["founders"]):
            founderId = ObjectId(founder)
            founderData  = await users_collection.find_one({"_id": founderId})
            if founderData:
                startup["founders"][i] = founderData

    if startup is None:
        raise HTTPException(status_code=404, detail="Startup not found")
    return StartupOut(**startup)

async def addStartup(startup: Startup):
    startup = startup.dict()
    for i, item in enumerate(startup["founders"]):
        startup["founders"][i] = ObjectId(item)  # Fix conversion to ObjectId
    
    if startup["previous_fundings"]:
        for i, item in enumerate(startup["previous_fundings"]):
            if "investors" in item and item["investors"] is not None:
                for j, investor in enumerate(item["investors"]):
                    if "investorId" in investor and investor["investorId"] is not None:
                        investor["investorId"] = ObjectId(investor["investorId"])

    if startup["equity_split"]:
        for i, item in enumerate(startup["equity_split"]):
            if "userId" in item and item["userId"] is not None:
                item["userId"] = ObjectId(item["userId"])

    founder_ids = startup["founders"]

    createsStartup = await startups_collection.insert_one(startup)
    startupId = str(createsStartup.inserted_id)

    for founder_id in founder_ids:
        await users_collection.update_one(
            {"_id": ObjectId(founder_id)},
            {"$set": {"currentStartup": ObjectId(startupId)}}
        )

    return JSONResponse({
        "message": "Startup created successfully",
        "startupId": str(startupId)
    }, status_code=201)

async def deleteStartup(startupId: str):
    try:
        startup_oid = ObjectId(startupId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid startup_id format")
    
    # Delete the startup document
    delete_result = await startups_collection.delete_one({"_id": startup_oid})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Startup not found")
    
    # Update all user documents where currentStartup equals this startup ObjectId
    await users_collection.update_many(
        {"currentStartup": startup_oid},
        {"$unset": {"currentStartup": ""}}
    )
    
    # Return a 204 No Content response
    return Response(status_code=status.HTTP_204_NO_CONTENT)