from config.database import investors_collection,users_collection
from bson import ObjectId
from models.InvestorModel import Investor,InvestorOut
from fastapi import HTTPException
from fastapi.responses import JSONResponse

async def getAllInvestors():
    investors = await investors_collection.find().to_list()

    for investor in investors:
        if "userId" in investor and isinstance(investor["userId"], ObjectId):
            user = await users_collection.find_one({"_id": investor["userId"]})
            investor["userId"] = str(investor["userId"])
        if user:
            user["_id"] = str(user["_id"])
            investor["user"] = user

    return [InvestorOut(**investor) for investor in investors]


async def getInvestorById(investorId: str):
    investor = await investors_collection.find_one({"_id": ObjectId(investorId)})
    if investor is None:        
        raise HTTPException(status_code=404, detail="Investor not found")
    if "userId" in investor and isinstance(investor["userId"], ObjectId):
        user = await users_collection.find_one({"_id": investor["userId"]})
        investor["userId"] = str(investor["userId"])
    if user:
        user["_id"] = str(user["_id"])
        investor["user"] = user
    return InvestorOut(**investor)


async def addInvestor(investor: Investor):
    createInvestor = await investors_collection.insert_one(investor.dict(exclude_unset=True))
    investorId = str(createInvestor.inserted_id)
    return JSONResponse({
        "message": "Entrepreneur created successfully",
        "entrepreneurId": str(investorId)
    },status_code=201)

# The parameter exclude_unset=True in investor.dict(exclude_unset=True) tells Pydantic to only include the fields that were explicitly set when creating the model instance, and exclude any default values that haven't been provided. This is useful for minimizing the data that gets inserted into the database, as it prevents unnecessary fields with default values from being sent.