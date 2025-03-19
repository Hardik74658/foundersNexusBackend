from pydantic import BaseModel, Field, validator
from typing import Optional,List,Dict,Any
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Field	Data Type	Description
# id	UUID	Unique identifier for the post
# user_id	UUID	User ID of the post creator
# content	Text	Text content of the post
# image_url	String	Optional image URL associated with the post
# likes	List of UUIDs	List of user IDs who liked the post
# comments	List of UUIDs	List of comment IDs associated with the post
# created_at	DateTime	Timestamp when the post was created
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

class Post(BaseModel):
    userId: str
    content: str
    image_url: Optional[str] = None
    likes: List[str] = []
    comments: List[str] = []
    created_at: datetime = Field(default_factory=current_time_ist)
    updated_at: datetime = Field(default_factory=current_time_ist)

    
    

class PostOut(Post):
    id: str = Field(alias="_id")

    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("userId", pre=True, always=True)
    def convert_user_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("likes", pre=True, always=True)
    def convert_likes(cls, v):
        return [convert_objectid_to_str(like) for like in v]
    
    @validator("comments", pre=True, always=True)
    def convert_comments(cls, v):
        return [convert_objectid_to_str(comment) for comment in v]