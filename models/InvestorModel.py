from pydantic import BaseModel,Field,validator
from bson import ObjectId
from typing import Optional,Dict,List,Any
from models.UserModel import User
# import datetime

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

def convert_objectid_to_str(value):
    if isinstance(value, ObjectId):
        print(value)
        return str(value)
    return value



def convert_str_to_objectid(value):
    if isinstance(value, str):
        return ObjectId(value)
    return value


class Investor(BaseModel):
    userId: str
    investor_type: str = Field(..., example="Angel")  # "Angel", "VC", "Corporate", "Government"
    investment_interests: List[str] = Field(default_factory=list, example=["SaaS", "Biotech"])
    previous_investments: List[Dict[str, str]] = Field(
        default_factory=list,
        example=[{"startup_id": "uuid-456", "startup_name": "StartupTwo", "investment_amount": "50000", "date": "2021-05-20"}]
    )
    # preferred_funding_stage: str = Field(..., example="Seed")
    contact_details: Optional[str] = Field(None, example="Encrypted Contact Info")

    # @validator("userId", pre=True)
    # def convert_founders(cls, v):
    #     return convert_str_to_objectid(v)
    
    # @validator("previous_investments", pre=True, always=True)
    # def convert_startup_ids_to_strings(cls, value):
    #     if value:
    #         for i, item in enumerate(value):
    #             if "startup_id" in item:
    #                 convert_objectid_to_str(item["startup_id"])
    #     return value




class InvestorOut(Investor):
    id: str = Field(alias="_id")
    userId: str 
    user: Optional[Dict[str, Any]] = None
    previous_investments: Optional[List[Dict[str, Any]]] = None
    funds_available: Optional[float] = None


    @validator("id",pre=True, always=True)
    def convert_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("userId",pre=True, always=True)
    def convert_user_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("user", pre=True, always=True)
    def convert_nested_objectid(cls, v):
        if isinstance(v, dict) and "_id" in v:
            v["_id"] = str(v["_id"])  
        return v        
   
    @validator("previous_investments", pre=True, always=True)
    def convert_startup_ids_to_strings(cls, value):
        if value and isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, dict):
                    processed_item = {}
                    for k, v in item.items():
                        if k == "startup_id" and v is not None:
                            processed_item[k] = convert_objectid_to_str(v)
                        else:
                            processed_item[k] = v
                    result.append(processed_item)
                else:
                    result.append(item)
            return result
        return value






