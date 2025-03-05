from pydantic import BaseModel,Field,validator 
from bson import ObjectId

class Role(BaseModel):
    name:str
    description:str


class RoleOut(Role):
    id:str = Field(alias="_id")
    
    @validator("id",pre=True,always=True)
    def convert_objectid(cls,v):
        if isinstance(v,ObjectId):
            return str(v)
        return v