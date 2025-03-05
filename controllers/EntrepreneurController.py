from config.database import entrepreneurs_collection,users_collection
from models.EntrepreneurModel import Entrepreneur, EntrepreneurOut
from bson import ObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse


async def getAllEntrepreneurs():
    entrepreneurs = await entrepreneurs_collection.find().to_list()

    for entrepreneur in entrepreneurs:
        if "userId" in entrepreneur and isinstance(entrepreneur.userId, ObjectId):
            user = await users_collection.find_one({"_id": entrepreneur.userId})
            entrepreneur["userId"] = str(entrepreneur.userId)
        if user:
            user["_id"] = str(user["_id"])
            entrepreneur["user"] = user

    return [EntrepreneurOut(**entrepreneur) for entrepreneur in entrepreneurs]

async def addEntrepreneur(entrepreneur:Entrepreneur):
    entrepreneur.userId = ObjectId(entrepreneur["userId"])
    entrepreneur_id = await entrepreneurs_collection.insert_one(entrepreneur).inserted_id
    return JSONResponse({
        "message": "Entrepreneur created successfully",
        "entrepreneurId": str(entrepreneur_id)
    },status_code=201)


async def getEntrepreneurById(entrepreneurId:str):
    entrepreneur = await entrepreneurs_collection.find_one({"_id": ObjectId(entrepreneurId)})
    if entrepreneur is None:
        raise HTTPException(status_code=404, detail="Entrepreneur not found")
    
    if "userId" in entrepreneur and isinstance(entrepreneur["userId"], ObjectId):
        user = await users_collection.find_one({"_id": entrepreneur["userId"]})
        entrepreneur["userId"] = str(entrepreneur["userId"])
    if user:
        user["_id"] = str(user["_id"])
        entrepreneur["user"] = user
    
    return EntrepreneurOut(**entrepreneur)
