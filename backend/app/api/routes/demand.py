"""
API routes for demand heatmap data
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from app.db.session import get_db
from app.models.driver import Driver
from app.models.ride import RideRequest
from app.services.demand_service import (
    get_zones,
    aggregate_zone_demand,
    Zone,
    ZoneDemand
)
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/zones", response_model=List[Zone])
async def get_demand_zones():
    """
    Get all defined geographic zones
    Returns 6x6 grid (36 zones) covering Bangalore
    """
    zones = get_zones()
    return zones


@router.get("/heatmap", response_model=List[ZoneDemand])
async def get_demand_heatmap(db: Session = Depends(get_db)):
    """
    Get current demand metrics for all zones
    
    Returns demand score (0-1) for each zone based on:
    - Current ride requests in the zone
    - Online driver availability
    - Predicted demand for next period
    """
    # Get zones
    zones = get_zones()
    
    # Get current pending ride requests
    pending_rides = db.query(RideRequest).filter(
        RideRequest.status == 'pending'
    ).all()
    
    # Convert to dicts for processing
    rides_data = [{
        'pickup_lat': float(ride.pickup_location_lat),
        'pickup_lng': float(ride.pickup_location_lng)
    } for ride in pending_rides]
    
    # Get online drivers
    online_drivers = db.query(Driver).filter(
        Driver.online_status == True
    ).all()
    
    drivers_data = [{
        'lat': float(driver.current_location_lat) if driver.current_location_lat else 0,
        'lng': float(driver.current_location_lng) if driver.current_location_lng else 0,
        'online_status': driver.online_status
    } for driver in online_drivers if driver.current_location_lat]
    
    # Aggregate demand by zone
    current_time = datetime.now()
    zone_demands = aggregate_zone_demand(zones, rides_data, drivers_data, current_time)
    
    logger.info(f"Generated heatmap for {len(zone_demands)} zones")
    
    return zone_demands


@router.get("/hotspots")
async def get_demand_hotspots(top_n: int = 5, db: Session = Depends(get_db)):
    """
    Get top N zones with highest demand
    Useful for driver positioning recommendations
    """
    # Get heatmap data
    zone_demands = await get_demand_heatmap(db)
    
    # Sort by demand score
    sorted_zones = sorted(zone_demands, key=lambda x: x.demand_score, reverse=True)
    
    # Get top N
    hotspots = sorted_zones[:top_n]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "top_zones": [
            {
                "zone_id": zone.zone_id,
                "demand_score": zone.demand_score,
                "requests": zone.request_count,
                "drivers": zone.driver_count,
                "predicted_demand": zone.predicted_demand,
                "recommendation": "High demand area - consider positioning drivers here"
            }
            for zone in hotspots
            if zone.demand_score > 0.3  # Only show meaningful hotspots
        ]
    }
