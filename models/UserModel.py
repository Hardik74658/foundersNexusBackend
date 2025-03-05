from pydantic import BaseModel,Field,validator
from bson import ObjectId
from typing import Optional, Dict, Any
import bcrypt   #pip install bcrypt

class User(BaseModel):
    fullName:str
    email:str
    password:str
    age:Optional[int]=None
    profilePicture:Optional[str] = ""
    bio:str
    location:str
    roleId:str
    isVerified:Optional[bool] = False
    isActive:Optional[bool] = True


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

    @validator("id",pre=True,always=True)
    def convert_id(cls,v):
        if isinstance(v,ObjectId):
            return str(v)
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