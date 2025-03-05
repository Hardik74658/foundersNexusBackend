from config.database import roles_collection
from models.RoleModel import Role,RoleOut
from bson import ObjectId

async def getAllRoles():
    roles = await roles_collection.find().to_list()
    return [RoleOut(**role) for role in roles]

async def addRole(role:Role):
    result = await roles_collection.insert_one(role.dict())
    print(result)
    return {"message":"user created successfully!!"}

async def deleteRole(roleId:str):
    result = await roles_collection.delete_one({"_id":ObjectId(roleId)})
    print(result)
    return {"message":"role deleted successfully!!"}


async def getRoleById(roleId:str):
    result = await roles_collection.find_one({"_id":ObjectId(roleId)})
    print(result)
    return RoleOut(**result)