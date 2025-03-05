from models.UserModel import User,UserOut,UserLogin
from config.database import users_collection,roles_collection
from bson import ObjectId
import bcrypt
from fastapi import HTTPException
from fastapi.responses import JSONResponse


async def getAllUsers():
    users = await users_collection.find().to_list()

    for user in users:
        
        if "roleId" in user and isinstance(user["roleId"],ObjectId):
            role = await roles_collection.find_one({"_id": user["roleId"]})
            user["roleId"] = str(user["roleId"])
        if role:
            role["_id"]=str(role["_id"])
            user["role"]=role        

    return [UserOut(**user) for user in users]

async def addUser(user:User):
    user.roleId = ObjectId(user.roleId)
    result = await users_collection.insert_one(user.dict())
    return JSONResponse(
        content={"message": "user created successfully", "user": str(result.inserted_id)},
        status_code=201
    )


async def deleteUser(userId:str):
    foundUser = await users_collection.delete_one({"_id":ObjectId(userId)})
    if foundUser is None:
        raise HTTPException(status_code=404,detail="User not found")
    return JSONResponse(
        content={"message": "user deleted successfully", "deletedUserCount": str(foundUser.deleted_count)},
        status_code=204
    )

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