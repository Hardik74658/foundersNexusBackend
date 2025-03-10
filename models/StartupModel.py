from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# IST timezone and helper function
IST = ZoneInfo("Asia/Kolkata")
def current_time_ist():
    return datetime.now(IST)

# Helper function to convert ObjectId to string
def convert_objectid_to_str(value):
    if isinstance(value, ObjectId):
        return str(value)
    return value

# Startup model (as stored in MongoDB)
class Startup(BaseModel):
    startup_name: str
    description: str
    industry: str
    website: Optional[str] = None
    founders: List[str]  
    market_size: str
    previous_fundings: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        example=[
            {
                "startup_name": "StartupOne",
                "stage": "Seed",
                "amount": "500000",
                "date": "2023-06-15",
                "investors": [ObjectId("60f8c2a5b3e2a123456789ac"), "External Investor X"]
            },
            {
                "startup_name": "StartupOne",
                "stage": "Series A",
                "amount": "5000000",
                "date": "2024-01-20",
                "investors": [ObjectId("60f8c2a5b3e2a123456789ae")]
            }
        ]
    )
    equity_split: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        example=[
            {
                "type": "Founder",
                "founder_id": ObjectId("60f8c2a5b3e2a123456789ab"),
                "name": "Alice Doe",
                "equity_percentage": "40%"
            },
            {
                "type": "Founder",
                "founder_id": ObjectId("60f8c2a5b3e2a123456789bb"),
                "name": "Bob Smith",
                "equity_percentage": "40%"
            },
            {
                "type": "Investor",
                "investor_id": ObjectId("60f8c2a5b3e2a123456789af"),
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

# StartupOut model for API responses with conversions
class StartupOut(Startup):
    id: str = Field(alias="_id")  # Startup document ID from MongoDB

    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        return convert_objectid_to_str(v)

    @validator("founders", pre=True, each_item=True)
    def convert_founders(cls, v):
        return convert_objectid_to_str(v)

    @validator("previous_fundings", pre=True)
    def convert_previous_fundings(cls, v):
        if not v:
            return v
        for record in v:
            # No funding_id is expected now
            if "investors" in record:
                record["investors"] = [convert_objectid_to_str(inv) for inv in record["investors"]]
        return v

    @validator("equity_split", pre=True)
    def convert_equity_split(cls, v):
        if not v:
            return v
        for record in v:
            # For founders, convert founder_id; for investors, convert investor_id if present
            if record.get("type") == "Founder" and "founder_id" in record:
                record["founder_id"] = convert_objectid_to_str(record["founder_id"])
            elif record.get("type") == "Investor" and "investor_id" in record:
                record["investor_id"] = convert_objectid_to_str(record["investor_id"])
        return v

