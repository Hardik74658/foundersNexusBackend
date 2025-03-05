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




# class EntrepreneurModel(User):
#     education_background: List[Dict[str, str]] = Field(
#         default_factory=list,
#         example=[{"degree": "MBA", "institution": "Harvard", "year": "2020", "field_of_study": "Business"}]
#     )
#     skills: List[str] = Field(default_factory=list, example=["Programming", "Marketing"])
#     area_of_interest: List[str] = Field(default_factory=list, example=["Fintech", "HealthTech"])
#     work_experience: List[Dict[str, str]] = Field(
#         default_factory=list,
#         example=[{"company_name": "TechCorp", "role": "Developer", "duration": "2 years", "description": "Developed X"}]
#     )
#     previous_startups: List[Dict[str, str]] = Field(
#         default_factory=list,
#         example=[{"startup_id": "uuid-123", "startup_name": "StartupOne", "role_in_startup": "Founder", "duration": "1 year"}]
#     )
#     certifications: Optional[List[str]] = Field(default_factory=list, example=["PMP", "AWS Certified"])
#     portfolio_links: Optional[List[str]] = Field(default_factory=list, example=["https://linkedin.com/in/johndoe"])




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