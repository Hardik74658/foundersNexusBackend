from pydantic import BaseModel,Field,validator
from bson import ObjectId
from typing import Optional,List,Dict,Any
from models.UserModel import User


# class Entrepreneur(BaseModel):
#     userId : str
#     educationalBackground : Optional[List[Dict[str, Any]]] = None
#     skills : Optional[List[str,Any]]=None
#     areaOfInterest : Optional[List[str]] = None
#     workExperience : Optional[List[str, Any]] = None
#     previousStartups : Optional[List[str, Any]] = None
#     certifications : Optional[List[str]] = None
#     portfolioLinks : Optional[List[str]] = None


def convert_objectid_to_str(value):
    if isinstance(value, ObjectId):
        return str(value)
    return value

def convert_str_to_objectid(value):
    if isinstance(value, str):
        return ObjectId(value)
    return value


class Entrepreneur(BaseModel):
    userId: str
    educationalBackground: List[Dict[str, str]] = Field(
        default_factory=list,
        example=[{"degree": "MBA", "institution": "Harvard", "year": "2020"}]
    )
    skills: List[str] = Field(default_factory=list, example=["Programming", "Marketing"])
    area_of_interest: List[str] = Field(default_factory=list, example=["Fintech", "HealthTech"])
    workExperience: List[Dict[str, str]] = Field(
        default_factory=list,
        example=[{"company_name": "TechCorp", "role": "Developer", "duration": "2 years", "description": "Developed X"}]
    )
    previous_startups: List[Dict[str, str]] = Field(
        default_factory=list,
        example=[{"startup_id": None, "startup_name": "StartupOne", "role_in_startup": "Founder", "duration": "1 year"}]
    )
    certifications: Optional[List[str]] = Field(default_factory=list, example=["PMP", "AWS Certified"])
    portfolioLinks: Optional[List[str]] = Field(default_factory=list, example=["https://linkedin.com/in/johndoe"])

    # @validator("userId", pre=True)
    # def convert_founders(cls, v):
    #     return convert_str_to_objectid(v)
    
    # @validator("previous_startups", pre=True, always=True)  
    # def convert_startup_ids_to_strings(cls, value):
    #     if value:
    #         for i, item in enumerate(value):
    #             if item["startup_id"] is not None:
    #               return convert_str_to_objectid(item["startup_id"])
    #     return value
    

class EntrepreneurUpdate(BaseModel):
    educationalBackground: Optional[List[Dict[str, str]]] = None
    skills: Optional[List[str]] = None
    area_of_interest: Optional[List[str]] = None
    workExperience: Optional[List[Dict[str, str]]] = None
    previous_startups: Optional[List[Dict[str, str]]] = None
    certifications: Optional[List[str]] = None
    portfolioLinks: Optional[List[str]] = None


class EntrepreneurOut(Entrepreneur):
    id: str = Field(alias="_id")
    userId: str
    user: Optional[Dict[str, Any]] = None


    @validator("id",  pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    @validator("userId",  pre=True, always=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    @validator("user", pre=True, always=True)
    def convert_nested_objectid(cls, v):
        if isinstance(v, dict) and "_id" in v:
            v["_id"] = str(v["_id"])  
        return v


