from config.database import entrepreneurs_collection,users_collection
from models.EntrepreneurModel import Entrepreneur, EntrepreneurOut, EntrepreneurUpdate
from controllers.UserController import deleteUser
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException ,Response ,status
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

async def getAllEntrepreneurs():
    # Retrieve all entrepreneur documents from the collection
    entrepreneurs = await entrepreneurs_collection.find().to_list(length=None)

    for entrepreneur in entrepreneurs:
        # Check if the entrepreneur document has a "userId" field and if it is an ObjectId
        if "userId" in entrepreneur:
            user = await users_collection.find_one({"_id": ObjectId(entrepreneur["userId"])})
            if user:
                entrepreneur["user"] = user

    
    # Recursively convert all ObjectIds in the list to strings
    entrepreneurs = convert_objectid_to_str(entrepreneurs)
    
    # Convert each document to an EntrepreneurOut instance and return
    return [EntrepreneurOut(**entrepreneur) for entrepreneur in entrepreneurs]



# pipeline = [
#     {
#         "$lookup": {
#             "from": "users",                  # Collection to join with
#             "localField": "userId",           # Field from the entrepreneurs collection
#             "foreignField": "_id",            # Field from the users collection
#             "as": "user"                      # Output array field
#         }
#     },
#     {
#         "$unwind": "$user"                    # Unwind the user array (assumes each entrepreneur has one user)
#     },
#     {
#         "$addFields": {                      # Convert ObjectId fields to strings if needed
#             "userId": {"$toString": "$userId"},
#             "user._id": {"$toString": "$user._id"}
#         }
#     }
# ]

# result = await entrepreneurs_collection.aggregate(pipeline).to_list(length=None)
# return [EntrepreneurOut(**entrepreneur) for entrepreneur in result]





async def addEntrepreneur(entrepreneur: Entrepreneur):
    entrepreneur_dict = entrepreneur.dict()
    if entrepreneur_dict["previous_startups"]:
        for i, item in enumerate(entrepreneur_dict["previous_startups"]):
            if item["startup_id"] is not None:
                entrepreneur_dict["previous_startups"][i]["startup_id"] = ObjectId(item["startup_id"])  
    if entrepreneur_dict["userId"]:
        entrepreneur_dict["userId"] = ObjectId(entrepreneur_dict["userId"])
    stored_entrepreneur = await entrepreneurs_collection.insert_one(entrepreneur_dict)
    entrepreneur_id = stored_entrepreneur.inserted_id
    # print(entrepreneur_id)
    return JSONResponse(content={
        "message": "Entrepreneur created successfully",
        "entrepreneurId": str(entrepreneur_id)
    }, status_code=201)

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


async def deleteEntrepreneur(entrepreneurId:str):
    entrepreneur = await entrepreneurs_collection.find_one({"_id": ObjectId(entrepreneurId)})
    if entrepreneur is None:
        raise HTTPException(status_code=404, detail="Entrepreneur not found")
    else:
        try:
            deleted_user = await users_collection.delete_one({"_id": ObjectId(entrepreneur["userId"])})
            deleted_entrepreneur = await entrepreneurs_collection.delete_one({"_id": ObjectId(entrepreneurId)})
        except:
            raise HTTPException(status_code=500, detail="Something went wrong while deleting the entrepreneur")
    if deleted_user.deleted_count == 1 and deleted_entrepreneur.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        


async def getEnterpreneurByUserId(userId:str):
    # Check if the userId is a valid ObjectId
    if not ObjectId.is_valid(userId):
        raise HTTPException(status_code=400, detail="Invalid userId format")
    
    # Find the entrepreneur by userId
    entrepreneur = await entrepreneurs_collection.find_one({"userId": ObjectId(userId)})
    
    # If no entrepreneur is found, raise a 404 error
    if entrepreneur is None:
        raise HTTPException(status_code=404, detail="Entrepreneur not found")
    
    # Convert ObjectId to string for the response
    entrepreneur["_id"] = str(entrepreneur["_id"])
    
    return EntrepreneurOut(**entrepreneur)

async def updateEntrepreneur(userId: str, entrepreneur_update: EntrepreneurUpdate):
    try:
        # Check if entrepreneur exists
        entrepreneur = await entrepreneurs_collection.find_one({"userId": ObjectId(userId)})
        if not entrepreneur:
            raise HTTPException(status_code=404, detail="Entrepreneur not found")

        # Create update dict with only provided fields
        update_data = {
            k: v for k, v in entrepreneur_update.dict(exclude_unset=True).items()
            if v is not None
        }

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No valid fields to update"
            )

        # Update the entrepreneur
        update_result = await entrepreneurs_collection.update_one(
            {"userId": ObjectId(userId)},
            {"$set": update_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Entrepreneur update failed"
            )

        # Get and return updated entrepreneur
        updated_entrepreneur = await entrepreneurs_collection.find_one({"userId": ObjectId(userId)})
        
        # Get associated user data
        if "userId" in updated_entrepreneur:
            user = await users_collection.find_one({"_id": updated_entrepreneur["userId"]})
            if user:
                user = convert_objectid_to_str(user)
                updated_entrepreneur["user"] = user

        updated_entrepreneur = convert_objectid_to_str(updated_entrepreneur)
        return EntrepreneurOut(**updated_entrepreneur)

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid entrepreneur ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))