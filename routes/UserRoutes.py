from fastapi import APIRouter
from models.UserModel import User,UserLogin
from controllers.UserController import getAllUsers,getUserById,deleteUser,addUser,loginUser

router = APIRouter()

@router.get("/users/")
async def get_all_users():
    return await getAllUsers()



@router.post("/users/")
async def add_user(user:User):
    return await addUser(user)


@router.get("/users/{userId}")
async def get_user_by_id(userId:str):
    return await getUserById(userId)

@router.delete("/users/{userId}")
async def delete_user(userId:str):
    return await deleteUser(userId)

@router.post("/user/login/")
async def login(user:UserLogin):
    return await loginUser(user)