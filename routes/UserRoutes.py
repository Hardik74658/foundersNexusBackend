from fastapi import APIRouter, File, Form, UploadFile
from models.UserModel import User, UserLogin, ResetPasswordReq, UserOut, UserUpdate
from controllers.UserController import (
    addUserWithFile, getAllUsers, getUserById, deleteUser, addUser, loginUser, toggleFollow,
    getFollowersByUserId, getFollowingByUserId, forgotPassword, resetPassword,
    getUsersByRole, updateUser,
)

router = APIRouter()

@router.get("/users/",tags=["Users"])
async def get_all_users():
    return await getAllUsers()


@router.get("/users/founders/", tags=["Users"])
async def get_entrepreneurs():
    return await getUsersByRole("Founder")

@router.get("/users/investors/", tags=["Users"])  # Add this line to handle trailing slash
async def get_investors():
    return await getUsersByRole("Investor")

@router.post("/users", tags=["Users"], include_in_schema=False)
async def create_user_with_file_no_trailing_slash(
    fullName: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    age: int = Form(None),
    bio: str = Form(...),
    location: str = Form(...),
    roleId: str = Form(...),
    profilePicture: UploadFile = File(None),
    coverPicture: UploadFile = File(None)
):
    # Log incoming request for debugging
    # print("Route: /users - create_user_with_file_no_trailing_slash")
    return await addUserWithFile(
        fullName, email, password, age, profilePicture, coverPicture, bio, location, roleId
    )

@router.post("/users/", tags=["Users"])
async def create_user_with_file(
    fullName: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    age: int = Form(None),
    bio: str = Form(...),
    location: str = Form(...),
    roleId: str = Form(...),
    profilePicture: UploadFile = File(None),
    coverImage: UploadFile = File(None)
):
    # Log incoming request for debugging
    # print("Route: /users/ - create_user_with_file")
    return await addUserWithFile(
        fullName, email, password, age, profilePicture, coverImage, bio, location, roleId
    )

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

@router.put("/users/{userId}", tags=["Users"])
async def update_user(userId: str, user: UserUpdate):
    return await updateUser(userId, user)
