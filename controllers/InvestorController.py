from config.database import investors_collection,users_collection
from bson import ObjectId
from models.InvestorModel import Investor,InvestorOut
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


async def getAllInvestors():
    investors = await investors_collection.find().to_list()

    for investor in investors:
        if "userId" in investor:
            user = await users_collection.find_one({"_id": ObjectId(investor["userId"])})

        if user:
            investor["user"] = user

    investors = convert_objectid_to_str(investors)
    # print(investors)
    return [InvestorOut(**investor) for investor in investors]


async def getInvestorById(investorId: str):
    investor = await investors_collection.find_one({"_id": ObjectId(investorId)})
    if investor is None:        
        raise HTTPException(status_code=404, detail="Investor not found")
    if "userId" in investor:
        user = await users_collection.find_one({"_id": ObjectId(investor["userId"])})
    if user:
        investor["user"] = user

    investor = convert_objectid_to_str(investor)
    return InvestorOut(**investor)


async def addInvestor(investor: Investor):
    investor = investor.dict()
    if investor["userId"]:
        investor["userId"] = ObjectId(investor["userId"])
    if investor["previous_investments"]:
        for i, item in enumerate(investor["previous_investments"]):
            if "startup_id" in item and item["startup_id"] is not None:
                investor["previous_investments"][i]["startup_id"] = ObjectId(item["startup_id"])
    createInvestor = await investors_collection.insert_one(investor)
    investorId = str(createInvestor.inserted_id)
    return JSONResponse({
        "message": "Investor created successfully",
        "investorId": str(investorId)
    },status_code=201)

async def deleteInvestor(investorId: str):
    investor = await investors_collection.find_one({"_id": ObjectId(investorId)})
    if investor is None:
        raise HTTPException(status_code=404, detail="Investor not found")
    try:
        deleted_user = await users_collection.delete_one({"_id": ObjectId(investor["userId"])})
        deleted_investor = await investors_collection.delete_one({"_id": ObjectId(investorId)})
    except:
        raise HTTPException(status_code=500, detail="Failed to delete investor")
    if deleted_user.deleted_count == 1 and deleted_investor.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


# The parameter exclude_unset=True in investor.dict(exclude_unset=True) tells Pydantic to only include the fields that were explicitly set when creating the model instance, and exclude any default values that haven't been provided. This is useful for minimizing the data that gets inserted into the database, as it prevents unnecessary fields with default values from being sent.


