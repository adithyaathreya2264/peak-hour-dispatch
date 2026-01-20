from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime


class RideRequestBase(BaseModel):
    rider_name: Optional[str] = None
    pickup_location_lat: float
    pickup_location_lng: float
    dropoff_location_lat: float
    dropoff_location_lng: float


class RideRequestCreate(RideRequestBase):
    traffic_score: float = Field(default=0.5, ge=0.0, le=1.0)
    demand_multiplier: float = Field(default=1.0, ge=1.0, le=3.0)


class RideRequestUpdate(BaseModel):
    status: Optional[str] = None
    estimated_fare: Optional[float] = None
    estimated_distance: Optional[float] = None


class RideRequestResponse(RideRequestBase):
    ride_id: UUID4
    request_time: datetime
    estimated_fare: Optional[float]
    estimated_distance: Optional[float]
    traffic_score: float
    demand_multiplier: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TripOutcomeCreate(BaseModel):
    ride_id: UUID4
    driver_id: UUID4
    acceptance_probability: float
    accepted: bool
    incentive_given: bool = False
    incentive_type: Optional[str] = None
    incentive_amount: float = 0.0


class TripOutcomeResponse(BaseModel):
    outcome_id: UUID4
    ride_id: UUID4
    driver_id: UUID4
    acceptance_probability: float
    accepted: bool
    completed: bool
    incentive_given: bool
    incentive_type: Optional[str]
    incentive_amount: float
    rejection_reason: Optional[str]
    final_fare: Optional[float]
    trip_duration: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class IncentiveCreate(BaseModel):
    driver_id: UUID4
    ride_id: UUID4
    incentive_type: str
    amount: float
    conditions: Optional[str] = None


class IncentiveResponse(BaseModel):
    incentive_id: UUID4
    driver_id: UUID4
    ride_id: UUID4
    incentive_type: str
    amount: float
    conditions: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
