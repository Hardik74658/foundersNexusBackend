from fastapi import APIRouter
from models.UserModel import User, UserLogin, ResetPasswordReq, UserOut
from controllers.UserController import (
    getAllUsers, getUserById, deleteUser, addUser, loginUser, toggleFollow,
    getFollowersByUserId, getFollowingByUserId, forgotPassword, resetPassword,
    
)

router = APIRouter()

@router.get("/users/",tags=["Users"])
async def get_all_users():
    return await getAllUsers()

@router.post("/users/",tags=["Users"])
async def add_user(user:User):
    return await addUser(user)

@router.get("/users/{userId}",tags=["Users"])
async def get_user_by_id(userId:str):
    return await getUserById(userId)

@router.delete("/users/{userId}",tags=["Users"])
async def delete_user(userId:str):
    return await deleteUser(userId)

@router.post("/users/login/",tags=["Users"])
async def login(user:UserLogin):
    return await loginUser(user)

@router.get("/users/{userId}/followers")
async def get_followers_by_user_id(userId:str):
    return await getFollowersByUserId(userId)

@router.get("/users/{userId}/following")
async def get_following_by_user_id(userId:str):
    return await getFollowingByUserId(userId)

@router.get("/users/{userId}/{followeeId}")
async def toggle_follw_user(userId:str,followeeId:str):
    return await toggleFollow(userId,followeeId)

@router.post("/forgotpassword")
async def forgot_password(email: str):
    return await forgotPassword(email)

@router.post("/resetpassword")
async def reset_password(data: ResetPasswordReq):
    return await resetPassword(data)