from models.UserModel import User,UserOut,UserLogin
from config.database import users_collection,roles_collection,startups_collection
from bson import ObjectId
import bcrypt
from fastapi import HTTPException, Response, status
from fastapi.responses import JSONResponse
from utils.SendMail import send_mail


def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data

async def getAllUsers():
    users = await users_collection.find().to_list()

    for user in users:
        if "roleId" in user and isinstance(user["roleId"],ObjectId):
            role = await roles_collection.find_one({"_id": user["roleId"]})
            # print(role)
            user["roleId"] = str(user["roleId"])
        if role:
            role["_id"]=str(role["_id"])
            user["role"]=role        
        if "currentStartup" in user and isinstance(user["currentStartup"],ObjectId):
            startup = await startups_collection.find_one({"_id": user["currentStartup"]})
            user["currentStartup"] = startup

    users = convert_objectid_to_str(users)
    return [UserOut(**user) for user in users]

async def addUser(user:User):
    user.roleId = ObjectId(user.roleId)
    result = await users_collection.insert_one(user.dict())
    send_mail(user.email,"Welcome to our platform","You have been successfully registered to our platform")   
    return JSONResponse(
        content={"message": "user created successfully", "user": str(result.inserted_id)},
        status_code=201
    )


async def deleteUser(userId:str):
    foundUser = await users_collection.delete_one({"_id":ObjectId(userId)})
    if foundUser.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404,detail="User not found")
    

async def getUserById(userId:str):
    foundUser = await users_collection.find_one({"_id":ObjectId(userId)})
    if foundUser is None:
        raise HTTPException(status_code=404,detail="User not found")
    if "roleId" in foundUser and isinstance(foundUser["roleId"],ObjectId):
            role = await roles_collection.find_one({"_id": foundUser["roleId"]})
            foundUser["roleId"] = str(foundUser["roleId"])
    if role:
        role["_id"]=str(role["_id"])
        foundUser["role"]=role      
    return UserOut(**foundUser)


async def loginUser(user:UserLogin):
    foundUser = await users_collection.find_one({"email":user.email})
    if foundUser is None:
        raise HTTPException(status_code=404,detail="User not found")

    foundUser["_id"] = str(foundUser["_id"])
    foundUser["roleId"] = str(foundUser["roleId"])

    if "password" in foundUser and bcrypt.checkpw(user.password.encode('utf-8'),foundUser["password"].encode('utf-8')):
        role = await roles_collection.find_one({"_id":ObjectId(foundUser["roleId"])})
        foundUser["role"] = role
        return {"message":"user login success","user":UserOut(**foundUser)}
    else:
        raise HTTPException(status_code=404,detail="Invalid email or password")