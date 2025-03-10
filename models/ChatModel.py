from pydantic import Field ,BaseModel,validator
from bson import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

def current_time_ist():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

# Chat Model
# Field	Data Type	Description
# id	UUID	Unique identifier for the message
# sender_id	UUID	User ID of the sender
# receiver_id	UUID	User ID of the receiver
# message_body	Text	Content of the message
# timestamp	DateTime	Timestamp when the message was sent
# is_read	Boolean	Indicates if the message has been read


def convert_objectid_to_str(value):
    if isinstance(value, ObjectId):
        return str(value)
    return value
def convert_str_to_objectid(value):
    if isinstance(value,str):
        return ObjectId(value)

class Chat(BaseModel):
    sender_id: str
    receiver_id: str
    message_body: str
    timestamp: Optional[datetime] = Field(default_factory=current_time_ist)
    is_read: Optional[bool] = False
    
     
    # @validator("role_id",pre=True,always=True)
    # def convert_objectId(cls,v):
    #     if isinstance(v,ObjectId):
    #         return str(v)
    #     return v

    @validator("sender_id",pre=True,always=True)
    def convert_sender_id(cls,v):
        return convert_str_to_objectid(v)
    
    @validator("receiver_id",pre=True,always=True)
    def convert_receiver_id(cls,v):
        return convert_str_to_objectid(v)
    
class ChatOut(Chat):
    id:str = Field(alias="_id")
    @validator("id",pre=True,always=True)
    def convert_id(cls,v):
        return convert_objectid_to_str(v)
    
    @validator("sender_id",pre=True,always=True)
    def convert_sender_id(cls,v):
        return convert_objectid_to_str(v)
    
    @validator("receiver_id",pre=True,always=True)
    def convert_receiver_id(cls,v):
        return convert_objectid_to_str(v)