from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Startup Model
# Field	Data Type	Description
# id	UUID	Unique identifier for the startup
# startup_name	String	Name of the startup
# description	Text	Detailed overview of what the startup does (explains what the startup actually does)
# industry	String	Market sector of the startup
# website	String	Startup's website URL
# logo_url	Optional[String]	URL to the startup's logo
# founders	List of UUIDs	List of entrepreneur user IDs (founders)
# market_size	String	Approximate potential market size
# revenue_model	Optional[String]	Revenue generation model (optional; updated when pitch is added)
# contact_details	Optional[String]	Contact details for further inquiries (optional; used to redirect to founders’ chat)
# previous_fundings	Optional[List of Dict]	List of past funding rounds; each record includes:
# - startup_name, stage, amount, date
# - investors: List of investor IDs (internal) or names (external)
# equity_split	Optional[List of Dict]	Equity distribution; each record includes:
# - For founders: founder_id, name, equity_percentage
# - For investors: investor_id, name, equity_percentage
# - For ESOP: name, equity_percentage
# created_at	DateTime	Timestamp of startup creation
# updated_at	DateTime	Timestamp for last update


# IST timezone and helper function
IST = ZoneInfo("Asia/Kolkata")
def current_time_ist():
    return datetime.now(IST)

# Helper functions for conversion
def convert_objectid_to_str(value):
    if isinstance(value, ObjectId):
        return str(value)
    return value

def convert_str_to_objectid(value):
    if isinstance(value, str):
        return ObjectId(value)
    return value

def convert_objectid_to_str_recursively(data):
    """Recursively converts ObjectId instances in the data to strings."""
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str_recursively(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str_recursively(item) for item in data]
    return data

# Updated Startup model with integrated pitch details
class Startup(BaseModel):
    startup_name: str
    description: str                    # Describes what the startup actually does
    industry: str
    website: Optional[str] = None
    logo_url: Optional[str] = None     # URL to the startup's logo
    founders: List[str]                 # List of entrepreneur IDs (as strings or ObjectIds)
    market_size: str                    # Approximate market size
    revenue_model: Optional[str] = None # Revenue generation model (optional)
    previous_fundings: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        example=[
            {
                "startup_name": "StartupOne",
                "stage": "Seed",
                "amount": "500000",
                "date": "2023-06-15",
                "investors": [
                    {
                        "investorId":"60f8c2a5b3e2a123456789ac",
                        "investorName":"xyz"
                    }
                ]
            },
            {
                "startup_name": "StartupOne",
                "stage": "Series A",
                "amount": "5000000",
                "date": "2024-01-20",
                "investors": [
                    {
                        "investorId":"60f8c2a5b3e2a123456789ae",
                        "investorName":"xyz"
                    }
                ]
            }
        ]
    )
    equity_split: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        example=[
            {
                "type": "Founder",
                "userId": "60f8c2a5b3e2a123456789ab",
                "name": "Alice Doe",
                "equity_percentage": "40%"
            },
            {
                "type": "Founder",
                "userId": "60f8c2a5b3e2a123456789bb",
                "name": "Bob Smith",
                "equity_percentage": "40%"
            },
            {
                "type": "Investor",
                "userId": "60f8c2a5b3e2a123456789af",
                "name": "VC Firm X",
                "equity_percentage": "15%"
            },
            {
                "type": "ESOP",
                "name": "Employee Stock Pool",
                "equity_percentage": "5%"
            }
        ]
    )
    created_at: datetime = Field(default_factory=current_time_ist)
    updated_at: datetime = Field(default_factory=current_time_ist)


    # @validator("founders", pre=True)
    # def convert_founders(cls, v):
    #     if not isinstance(v, list):
    #         return v
    #     return [convert_str_to_objectid(item) for item in v]

    # @validator("previous_fundings", pre=True)
    # def convert_previous_fundings(cls, v):
    #     if not v:
    #         return v
    #     for record in v:
    #         if "investors" in record:
    #             record["investors"] = [convert_str_to_objectid(inv) for inv in record["investors"]]
    #     return v

    # @validator("equity_split", pre=True)
    # def convert_equity_split(cls, v):
    #     if not v:
    #         return v
    #     for record in v:
    #         if record.get("type") == "Founder" and "founder_id" in record:
    #             record["founder_id"] = convert_str_to_objectid(record["founder_id"])
    #         elif record.get("type") == "Investor" and "investor_id" in record:
    #             record["investor_id"] = convert_str_to_objectid(record["investor_id"])
    #     return v

# StartupOut model for API responses with conversion of ObjectIds to strings
class StartupOut(Startup):
    id: str = Field(alias="_id")  # MongoDB document ID
    founders: List[Dict[str,Any]] = None
    previous_fundings: Optional[List[Dict[str, Any]]] = None
    equity_split: Optional[List[Dict[str, Any]]] = None

    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        return convert_objectid_to_str(v)

    @validator("founders", pre=True)
    def convert_founders(cls, v):
        return convert_objectid_to_str_recursively(v) 

    @validator("previous_fundings", pre=True)
    def convert_previous_fundings(cls, v):
        return convert_objectid_to_str_recursively(v)

    @validator("equity_split", pre=True)
    def convert_equity_split(cls, v):
        return convert_objectid_to_str_recursively(v)

