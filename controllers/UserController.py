from models.UserModel import User,UserOut,UserLogin,ResetPasswordReq,UserUpdate
from config.database import users_collection,roles_collection,startups_collection
from bson import ObjectId
import bcrypt
from fastapi import File, Form, HTTPException, Response, UploadFile, status
from fastapi.responses import JSONResponse
from utils.SendMail import send_mail
from utils.CloudinaryUpload import upload_image_from_buffer
from utils.CometChatIntegration import register_user_with_cometchat
from bson.errors import InvalidId
from pydantic import EmailStr, ValidationError


import datetime
import jwt


def convert_objectid_to_str(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, bytes):
        try:
            # Try to decode bytes as UTF-8 first
            return data.decode('utf-8')
        except UnicodeDecodeError:
            # If that fails, use base64 encoding
            import base64
            return base64.b64encode(data).decode('ascii')
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data

def convert_datetime_to_str(data):
    """Recursively converts datetime objects in the data to strings."""
    if isinstance(data, datetime.datetime):  # Use the datetime class directly
        return data.isoformat()
    elif isinstance(data, dict):
        return {k: convert_datetime_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_datetime_to_str(item) for item in data]
    return data

# CRUD ON USERS

async def getAllUsers():
    users = await users_collection.find().to_list()

    for user in users:
        if "roleId" in user and isinstance(user["roleId"],ObjectId):
            role = await roles_collection.find_one({"_id": user["roleId"]})
            user["roleId"] = str(user["roleId"])
        if role:
            role["_id"]=str(role["_id"])
            user["role"]=role        
        if "currentStartup" in user and isinstance(user["currentStartup"],ObjectId):
            startup = await startups_collection.find_one({"_id": user["currentStartup"]})
            # Only assign the string ID to currentStartup
            user["currentStartup"] = str(user["currentStartup"])
            # Optionally, include the startup data under a different key
            # user["currentStartupData"] = startup
        if "password" in user:
            user["password"]=str(user["password"])

    users = convert_objectid_to_str(users)
    return [UserOut(**user) for user in users]

async def getUsersByRole(role_name: str):
    role = await roles_collection.find_one({"name": role_name})
    if not role:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found")

    role_id = role["_id"]
    users = await users_collection.find({"roleId": role_id}).to_list()

    for user in users:
        if "password" in user:
            user["password"] = str(user["password"])
        if "roleId" in user:
            user["roleId"] = str(user["roleId"])
        if "currentStartup" in user and isinstance(user["currentStartup"], ObjectId):
            startup = await startups_collection.find_one({"_id": user["currentStartup"]})
            user["currentStartupData"] = startup  # Populate nested startup details
            user["currentStartup"] = str(user["currentStartup"])  # Keep the ID as a string

    users = convert_objectid_to_str(users)
    return [UserOut(**user) for user in users]

async def addUser(user: User):
    user.roleId = ObjectId(user.roleId)
    result = await users_collection.insert_one(user.dict())
    user_id = str(result.inserted_id)

    # Register user with CometChat
    try:
        await register_user_with_cometchat(
            user_id=user_id,
            full_name=user.fullName,
            email=user.email
        )
    except Exception as e:
        # Log error but don't fail registration if CometChat integration fails
        print(f"Error registering user with CometChat: {str(e)}")

    send_mail(user.email, "Welcome to our platform", "You have been successfully registered to our platform")
    return JSONResponse(
        content={"message": "user created successfully", "user": user_id},
        status_code=201
    )

async def addUserWithFile(
    fullName: str = Form(...),
    email: EmailStr = Form(...),  # Validate email format
    password: str = Form(...),
    age: int = Form(None),
    profilePicture: UploadFile = File(None),
    coverImage: UploadFile = File(None),
    bio: str = Form(...),
    location: str = Form(...),
    roleId: str = Form(...),
):
    try:
        # Validate ObjectId format for roleId
        try:
            roleId_object = ObjectId(roleId)  # Convert roleId to ObjectId
        except InvalidId:
            raise HTTPException(status_code=422, detail="Invalid roleId format")

        user_data = {
            "fullName": fullName,
            "email": email,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),  # Hash password
            "age": age,
            "bio": bio,
            "location": location,
            "roleId": roleId_object,  # Store roleId as ObjectId
            "isVerified": False,
            "isActive": True,
            "followers": [],
            "following": [],
            "posts": [],
            "currentStartup": None,
        }

        profile_picture_url = ""
        # Upload profile picture if provided
        if profilePicture:
            print("Reading profilePicture...")
            profile_picture_url = await upload_image_from_buffer(profilePicture)
            user_data["profilePicture"] = profile_picture_url
        else:
            user_data["profilePicture"] = ""

        # Upload cover picture if needed (optional)
        if coverImage:
            print("Reading coverPicture...")
            user_data["coverImage"] = await upload_image_from_buffer(coverImage)
        else:
            user_data["coverImage"] = ""

        # Save to database
        result = await users_collection.insert_one(user_data)
        user_id = str(result.inserted_id)

        # Register user with CometChat
        try:
            await register_user_with_cometchat(
                user_id=user_id,
                full_name=fullName,
                profile_picture=profile_picture_url,
                email=email
            )
        except Exception as e:
            # Log error but don't fail registration if CometChat integration fails
            print(f"Error registering user with CometChat: {str(e)}")

        # Optional: Send welcome email
        send_mail(email, "Welcome to FoundersNexus", "You have been successfully registered.")

        return JSONResponse(
            content={"message": "User created successfully", "user": user_id},
            status_code=201
        )

    except ValidationError as ve:
        # Log validation errors for debugging
        print("Validation Error:", ve.errors())
        return JSONResponse(
            content={"error": "Validation error", "details": ve.errors()},
            status_code=422
        )
    except HTTPException as http_exc:
        # Log HTTP exceptions for debugging
        print("HTTP Exception:", http_exc.detail)
        raise http_exc
    except Exception as e:
        # Log unexpected errors for debugging
        print("Unexpected Error:", str(e))
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

async def deleteUser(userId:str):
    foundUser = await users_collection.delete_one({"_id":ObjectId(userId)})
    if foundUser.deleted_count == 1:
        # Optionally delete user from CometChat as well
        try:
            from utils.CometChatIntegration import CometChatService
            await CometChatService.delete_user(userId)
        except Exception as e:
            # Log the error but don't prevent user deletion
            print(f"Error deleting user from CometChat: {str(e)}")
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
    if "password" in foundUser:
        foundUser["password"]=str(foundUser["password"])
    foundUser = convert_objectid_to_str(foundUser)
    return UserOut(**foundUser)


# FUNCTIONALITIES ON USER

async def loginUser(user: UserLogin):
    print(user)
    foundUser = await users_collection.find_one({"email": user.email})
    if foundUser is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert ObjectId fields to strings
    foundUser = convert_objectid_to_str(foundUser)
    if "password" in foundUser and bcrypt.checkpw(user.password.encode('utf-8'), foundUser["password"].encode('utf-8')):
        foundUser["password"]=str(foundUser["password"])
        role = await roles_collection.find_one({"_id": ObjectId(foundUser["roleId"])})
        if role:
            role = convert_objectid_to_str(role)
        foundUser["role"] = role

        return {"message": "user login success", "user": UserOut(**foundUser), "success": True}
    else:
        raise HTTPException(status_code=404, detail="Invalid email or password")
    


async def toggleFollow(userId: str, followeeId: str):
    # Get the current user (the follower)
    current_user = await users_collection.find_one({"_id": ObjectId(userId)})
    if not current_user:
        raise HTTPException(404, "User Not Found")
    
    # Get the followee user (the one to be followed/unfollowed)
    followee = await users_collection.find_one({"_id": ObjectId(followeeId)})
    if not followee:
        raise HTTPException(404, "Followee User Not Found")
    
    # Check if current user's ObjectId is in the followee's "followers" array
    if ObjectId(followeeId) in current_user.get("followers", []):
        # Remove the follower from followee's followers array
        await users_collection.update_one(
            {"_id": ObjectId(userId)},
            {"$pull": {"followers": ObjectId(followeeId)}}
        )
        # Optionally, remove the followee from current user's following array
        await users_collection.update_one(
            {"_id": ObjectId(followeeId)},
            {"$pull": {"following": ObjectId(userId)}}
        )
        return {"message": "Follower Removed successfully"}
    else:
        # Add the follower to followee's followers array
        await users_collection.update_one(
            {"_id": ObjectId(userId)},
            {"$addToSet": {"followers": ObjectId(followeeId)}}
        )
        # Optionally, add the followee to current user's following array
        await users_collection.update_one(
            {"_id": ObjectId(followeeId)},
            {"$addToSet": {"following": ObjectId(userId)}}
        )
        return {"message": "Follower Added successfully"}



async def getFollowersByUserId(userId: str):
    user = await users_collection.find_one({"_id": ObjectId(userId)})
    if not user:
        raise HTTPException(404, "User Not Found")
    
    followersData = []
    if "followers" in user and isinstance(user["followers"], list):
        for follower in user["followers"]:
            try:
                # Ensure follower is a valid ObjectId
                follower_id = ObjectId(follower) if not isinstance(follower, ObjectId) else follower
                followerData = await users_collection.find_one({"_id": follower_id})
                if followerData:
                    followersData.append(followerData)
            except InvalidId:
                # Skip invalid follower IDs
                continue
    
    # Convert ObjectId fields and datetime objects to strings
    followersData = convert_objectid_to_str(followersData)
    followersData = convert_datetime_to_str(followersData)
    
    return JSONResponse(content={"followers": followersData}, status_code=200)

async def getFollowingByUserId(userId: str):
    user = await users_collection.find_one({"_id": ObjectId(userId)})
    if not user:
        raise HTTPException(404, "User Not Found")
    
    followingData = []
    if "following" in user and isinstance(user["following"], list):
        for followee in user["following"]:
            try:
                # Ensure followee is a valid ObjectId
                followee_id = ObjectId(followee) if not isinstance(followee, ObjectId) else followee
                followeeData = await users_collection.find_one({"_id": followee_id})
                if followeeData:
                    followingData.append(followeeData)
            except InvalidId:
                # Skip invalid followee IDs
                continue
    
    # Convert ObjectId fields and datetime objects to strings
    followingData = convert_objectid_to_str(followingData)
    followingData = convert_datetime_to_str(followingData)
    
    return JSONResponse(content={"following": followingData}, status_code=200)


# Forgot And Reset Pwd functionality With JWT Token

SECRET_KEY = "royal"

def generate_token(email: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {"sub": email, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


async def forgotPassword(email: str):
    foundUser = await users_collection.find_one({"email": email})
    if not foundUser:
        raise HTTPException(status_code=404, detail="Email not found")
    
    token = generate_token(email)
    resetLink = f"http://localhost:5173/resetpassword/{token}"
    body = f"""
    <html>
        <h1>HELLO THIS IS RESET PASSWORD LINK. IT EXPIRES IN 1 HOUR</h1>
        <a href="{resetLink}">RESET PASSWORD</a>
    </html>
    """
    subject = "RESET PASSWORD"
    send_mail(email, subject, body)
    return {"message": "Reset link sent successfully"}


async def resetPassword(data: ResetPasswordReq):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms="HS256")  # Payload: {"sub": "email...", "exp": ...}
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=421, detail="Token is not valid")
        
        hashed_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt())
        await users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
        
        return {"message": "Password updated successfully"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="The reset password link has expired. Please request a new one."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token provided")

async def updateUser(userId: str, user_update: UserUpdate):
    try:
        user = await users_collection.find_one({"_id": ObjectId(userId)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create update dict with only provided fields
        update_data = {
            k: v for k, v in user_update.dict(exclude_unset=True).items()
            if v is not None
        }

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No valid fields to update"
            )

        # Update the user
        update_result = await users_collection.update_one(
            {"_id": ObjectId(userId)},
            {"$set": update_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=400,
                detail="User update failed"
            )

        # Get and return updated user
        updated_user = await users_collection.find_one({"_id": ObjectId(userId)})
        updated_user = convert_objectid_to_str(updated_user)
        
        if "password" in updated_user:
            updated_user["password"] = str(updated_user["password"])

        return UserOut(**updated_user)

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def getRecentSignups(days: int = 7):
    """Get users who signed up in the last specified number of days"""
    # Calculate the date from which to fetch users
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # Query for users created after the cutoff date, sorted by creation date (newest first)
    recent_users = await users_collection.find(
        {"created_at": {"$gte": cutoff_date}}
    ).sort("created_at", -1).to_list(length=None)
    
    # Process users similar to getAllUsers() function
    for user in recent_users:
        if "roleId" in user and isinstance(user["roleId"], ObjectId):
            role = await roles_collection.find_one({"_id": user["roleId"]})
            user["roleId"] = str(user["roleId"])
            if role:
                role["_id"] = str(role["_id"])
                user["role"] = role
        
        if "currentStartup" in user and isinstance(user["currentStartup"], ObjectId):
            startup = await startups_collection.find_one({"_id": user["currentStartup"]})
            user["currentStartup"] = str(user["currentStartup"])
            if startup:
                user["currentStartupData"] = convert_objectid_to_str(startup)
        
        if "password" in user:
            user["password"] = str(user["password"])
    
    # Convert ObjectIds and datetimes to strings
    recent_users = convert_objectid_to_str(recent_users)
    
    return [UserOut(**user) for user in recent_users]