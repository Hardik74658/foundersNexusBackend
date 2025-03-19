from pydantic import BaseModel,Field,validator
from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any
import bcrypt   #pip install bcrypt
from zoneinfo import ZoneInfo 

def current_time_ist():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

# User Model
# Field	Data Type	Description
# id	UUID	Unique identifier for each user
# full_name	String	User's complete name
# email	String	Unique email address
# password	String	Bcrypt-encrypted password
# profile_picture	String	URL to the user's profile image
# bio	String	Brief biography
# location	String	User's location
# role	Enum	Role of the user: Entrepreneur or Investor
# followers	List of UUIDs	List of user IDs who follow this user
# following	List of UUIDs	List of user IDs that this user follows
# posts	List of UUIDs	List of post IDs created by the user
# current_startup	Optional[UUID]	ID of the startup the user is currently active in (if applicable)
# is_verified	Boolean	Indicates if the account is verified
# is_active	Boolean	Indicates if the account is active
# created_at	DateTime	Timestamp of account creation
# updated_at	DateTime	Timestamp for last update

class User(BaseModel):
    fullName:str
    email:str
    password:str
    age:Optional[int]=None
    profilePicture:Optional[str] = ""
    bio:str
    location:str
    roleId:str
    followers:Optional[list] = []
    following:Optional[list] = []
    posts:Optional[list] = []
    currentStartup:Optional[str] = None
    isVerified:Optional[bool] = False
    isActive:Optional[bool] = True
    created_at: datetime = Field(default_factory=current_time_ist)
    updated_at: datetime = Field(default_factory=current_time_ist)


    @validator("password",pre=True,always=True)
    def encrypt_password(cls,v):
        if v is None:
            return None
        return bcrypt.hashpw(v.encode("utf-8"),bcrypt.gensalt())
        

class UserOut(User):
    id:str = Field(alias="_id")
    # The role information is optional and is expected to be a dictionary.
    role: Optional[Dict[str, Any]] = None
    # Optional fields that you may not want to return in your API response.
    email: Optional[str] = None
    password: Optional[str] = None
    currentStartup: Optional[Dict[str,Any]] = None

    @validator("id",pre=True,always=True)
    def convert_id(cls,v):
        if isinstance(v,ObjectId):
            return str(v)
        return v
    
    @validator("currentStartup",pre=True,always=True)
    def convert_current_startup_id(cls,v):
        if isinstance(v,Dict) and "_id" in v:
            v["_id"] = str(v["_id"])
        return v
    
    @validator("role", pre=True, always=True)
    def convert_role_id_to_string(cls, value):
        """
        If the role is a dictionary and contains an "_id" field (from MongoDB),
        convert that _id to a string.
        This ensures that nested role IDs are also easier to handle.
        """
        if isinstance(value, dict) and "_id" in value:
            value["_id"] = str(value["_id"])
        return value


class UserLogin(BaseModel):
    email:str
    password:str