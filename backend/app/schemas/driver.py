from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime


class DriverBase(BaseModel):
    name: str
    phone: str


class DriverCreate(DriverBase):
    current_location_lat: Optional[float] = None
    current_location_lng: Optional[float] = None


class DriverUpdate(BaseModel):
    current_location_lat: Optional[float] = None
    current_location_lng: Optional[float] = None
    online_status: Optional[bool] = None
    earnings_today: Optional[float] = None
    earnings_last_hour: Optional[float] = None
    fatigue_score: Optional[float] = None


class DriverResponse(DriverBase):
    driver_id: UUID4
    current_location_lat: Optional[float]
    current_location_lng: Optional[float]
    online_status: bool
    acceptance_rate: float
    total_trips: int
    earnings_today: float
    earnings_last_hour: float
    fatigue_score: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DriverLocation(BaseModel):
    driver_id: UUID4
    latitude: float
    longitude: float
    online_status: bool
