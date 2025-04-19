from pydantic import BaseModel, Field, validator, HttpUrl, constr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from zoneinfo import ZoneInfo
from bson import ObjectId

# Helper functions
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

# Base PitchDeck model
class PitchDeck(BaseModel):
    title: str
    description: Optional[str] = None
    startupId: str
    file_url: str
    view_url: Optional[str] = None  # URL optimized for viewing in browser
    thumbnail_url: Optional[str] = None
    active: bool = False
    raise_until: Optional[date] = None
    target_amount: Optional[str] = None
    round: Optional[str] = None
    slides_count: Optional[int] = 0
    file_type: Optional[str] = None  # Store file extension
    external_link: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=current_time_ist)
    updated_at: datetime = Field(default_factory=current_time_ist)

# Model for creating a new pitch deck
class PitchDeckCreate(BaseModel):
    title: str
    description: Optional[str] = None
    startupId: str
    raise_until: Optional[date] = None
    target_amount: Optional[str] = None
    round: Optional[str] = None
    external_link: Optional[HttpUrl] = None

# Model for updating an existing pitch deck
class PitchDeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    raise_until: Optional[date] = None
    target_amount: Optional[str] = None
    round: Optional[str] = None
    external_link: Optional[HttpUrl] = None
    updated_at: datetime = Field(default_factory=current_time_ist)

# Output model for API responses
class PitchDeckOut(PitchDeck):
    id: str = Field(alias="_id")
    startup: Optional[Dict[str, Any]] = None
    
    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        return convert_objectid_to_str(v)
    
    @validator("startupId", pre=True, always=True)
    def convert_startup_id(cls, v):
        return convert_objectid_to_str(v)
    
    class Config:
        validate_by_name = True  # Updated from allow_population_by_field_name = True
