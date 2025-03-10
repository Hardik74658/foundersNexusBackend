from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Comment Model
# Field	Data Type	Description
# id	UUID	Unique identifier for the comment
# post_id	UUID	Reference to the associated Post
# user_id	UUID	User ID of the commenter
# content	Text	Text content of the comment
# created_at	DateTime	Timestamp when the comment was created
# updated_at	DateTime	Timestamp for last update

def current_time_ist():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

def convert_objectid_to_str(value):
    if isinstance(value, ObjectId):
        return str(value)
    return value

def convert_str_to_objectid(value):
    if isinstance(value, str):
        return ObjectId(value)
    return value

class Comment(BaseModel):
    post_id: str
    user_id: str
    content: str
    created_at: datetime = Field(default_factory=current_time_ist)
    updated_at: datetime = Field(default_factory=current_time_ist)
    
    @validator("post_id", pre=True, always=True)
    def convert_post_id(cls, v):
        return convert_str_to_objectid(v)
    
    @validator("user_id", pre=True, always=True)
    def convert_user_id(cls, v):
        return convert_str_to_objectid(v)
    

class CommentOut(Comment):
    id: str = Field(alias="_id")
    
    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("post_id", pre=True, always=True)
    def convert_post_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("user_id", pre=True, always=True)
    def convert_user_id(cls, v):
        return convert_objectid_to_str(v)