from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.ride import RideRequest, TripOutcome
from app.schemas.ride import (
    RideRequestCreate,
    RideRequestResponse,
    RideRequestUpdate,
    TripOutcomeCreate,
    TripOutcomeResponse
)
from app.utils.geo import haversine_distance, calculate_fare
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=RideRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_ride_request(ride: RideRequestCreate, db: Session = Depends(get_db)):
    """Create a new ride request"""
    try:
        # Calculate distance and fare
        distance = haversine_distance(
            ride.pickup_location_lat,
            ride.pickup_location_lng,
            ride.dropoff_location_lat,
            ride.dropoff_location_lng
        )
        
        fare = calculate_fare(
            distance,
            ride.traffic_score,
            ride.demand_multiplier
        )
        
        db_ride = RideRequest(
            **ride.dict(),
            estimated_distance=round(distance, 2),
            estimated_fare=fare
        )
        
        db.add(db_ride)
        db.commit()
        db.refresh(db_ride)
        
        logger.info(f"Created ride request: {db_ride.ride_id} - Distance: {distance:.2f}km, Fare: ₹{fare}")
        return db_ride
    
    except Exception as e:
        logger.error(f"Error creating ride request: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[RideRequestResponse])
async def get_ride_requests(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all ride requests"""
    query = db.query(RideRequest)
    
    if status_filter:
        query = query.filter(RideRequest.status == status_filter)
    
    rides = query.order_by(RideRequest.request_time.desc()).offset(skip).limit(limit).all()
    return rides


@router.get("/{ride_id}", response_model=RideRequestResponse)
async def get_ride_request(ride_id: str, db: Session = Depends(get_db)):
    """Get a specific ride request"""
    ride = db.query(RideRequest).filter(RideRequest.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride request not found")
    return ride


@router.patch("/{ride_id}", response_model=RideRequestResponse)
async def update_ride_request(
    ride_id: str,
    ride_update: RideRequestUpdate,
    db: Session = Depends(get_db)
):
    """Update ride request status"""
    ride = db.query(RideRequest).filter(RideRequest.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride request not found")
    
    update_data = ride_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ride, field, value)
    
    db.commit()
    db.refresh(ride)
    logger.info(f"Updated ride request: {ride_id}")
    return ride


@router.post("/outcomes", response_model=TripOutcomeResponse, status_code=status.HTTP_201_CREATED)
async def create_trip_outcome(outcome: TripOutcomeCreate, db: Session = Depends(get_db)):
    """Record trip outcome"""
    try:
        db_outcome = TripOutcome(**outcome.dict())
        db.add(db_outcome)
        db.commit()
        db.refresh(db_outcome)
        
        logger.info(f"Created trip outcome: {db_outcome.outcome_id}")
        return db_outcome
    
    except Exception as e:
        logger.error(f"Error creating trip outcome: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outcomes/", response_model=List[TripOutcomeResponse])
async def get_trip_outcomes(
    driver_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get trip outcomes"""
    query = db.query(TripOutcome)
    
    if driver_id:
        query = query.filter(TripOutcome.driver_id == driver_id)
    
    outcomes = query.offset(skip).limit(limit).all()
    return outcomes
