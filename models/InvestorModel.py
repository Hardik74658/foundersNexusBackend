from pydantic import BaseModel,Field,validator
from bson import ObjectId
from typing import Optional,Dict,List,Any
from models.UserModel import User

# id	UUID
# user_id	UUID
# investor_type	Enum
# funds_available	Float
# investment_interests	Array of Strings
# previous_investments	Array of Objects
# preferred_funding_stage	Enum
# contact_details	String
# created_at	DateTime
# updated_at	DateTime



class Investor(User):
    userId: str
    investor_type: str = Field(..., example="Angel")  # "Angel", "VC", "Corporate", "Government"
    investment_interests: List[str] = Field(default_factory=list, example=["SaaS", "Biotech"])
    previous_investments: List[Dict[str, str]] = Field(
        default_factory=list,
        example=[{"startup_id": "uuid-456", "startup_name": "StartupTwo", "investment_amount": "50000", "date": "2021-05-20"}]
    )
    preferred_funding_stage: str = Field(..., example="Seed")
    contact_details: Optional[str] = Field(None, example="Encrypted Contact Info")

class InvestorOut(Investor):
    id: str = Field(alias="_id")
    
    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    @validator("user", pre=True, always=True)
    def convert_user_id_to_string(cls, value):  
        if isinstance(value, dict) and "_id" in value:
            value["_id"]=str(value["_id"])
        return value
    
    
    @validator("previous_investments", pre=True, always=True)
    def convert_startup_ids_to_strings(cls, value):
        if value:
            for i, item in enumerate(value):
                if "startup_id" in item:
                    value[i]["startup_id"]=str(item["startup_id"])
        return value





    