from pydantic import BaseModel,Field,validator
from bson import ObjectId
from typing import Optional,List,Dict,Any


class Entrepreneur(BaseModel):
    userId : str
    educationalBackground : Optional[List[Dict[str, Any]]] = None
    skills : Optional[List[str,Any]]=None
    areaOfInterest : Optional[List[str]] = None
    workExperience : Optional[List[str, Any]] = None
    previousStartups : Optional[List[str, Any]] = None
    certifications : Optional[List[str]] = None
    portfolioLinks : Optional[List[str]] = None

class EntrepreneurOut(Entrepreneur):
    id: str = Field(alias="_id")
    user: Optional[Dict[str,Any]]=None

    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    @validator("user", pre=True, always=True)
    def convert_user_id(cls, v):
        if isinstance(v, Dict) and "_id" in v :
            v["_id"]=str(v["_id"])
        return v