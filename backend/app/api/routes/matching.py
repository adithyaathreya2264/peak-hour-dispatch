from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime
from app.db.session import get_db
from app.models.driver import Driver
from app.models.ride import RideRequest
from app.utils.geo import haversine_distance, estimate_eta, calculate_fare
from app.utils.scoring import calculate_overall_score
from app.core.config import settings
from app.core.logging import get_logger
from app.ml.inference.denial_predictor import get_predictor

router = APIRouter()
logger = get_logger(__name__)


class MatchRequest(BaseModel):
    ride_id: UUID4


class DriverMatch(BaseModel):
    driver_id: UUID4
    driver_name: str
    distance_km: float
    eta_minutes: int
    acceptance_probability: float
    overall_score: float
    score_breakdown: Dict[str, Any]
    prediction_source: str  # 'ml' or 'heuristic'


class MatchResponse(BaseModel):
    ride_id: UUID4
    matched_drivers: List[DriverMatch]


@router.post("/find-drivers", response_model=MatchResponse)
async def find_matching_drivers(
    request: MatchRequest,
    max_drivers: int = 5,
    db: Session = Depends(get_db)
):
    """
    Find and rank drivers for a ride request using acceptance-aware matching
    Now powered by ML-based acceptance probability prediction!
    """
    # Get ride request
    ride = db.query(RideRequest).filter(RideRequest.ride_id == request.ride_id).first()
    if not ride:
        return {"error": "Ride not found"}
    
    # Get online drivers
    online_drivers = db.query(Driver).filter(Driver.online_status == True).all()
    
    if not online_drivers:
        logger.warning("No online drivers available")
        return MatchResponse(ride_id=request.ride_id, matched_drivers=[])
    
    # Calculate average stats for fairness scoring
    avg_trips = sum(d.total_trips for d in online_drivers) / len(online_drivers) if online_drivers else 0
    avg_earnings = sum(float(d.earnings_today) for d in online_drivers) / len(online_drivers) if online_drivers else 0
    
    # Get ML predictor
    predictor = get_predictor()
    
    # Current hour for time-based features
    current_hour = datetime.now().hour
    
    driver_matches = []
    
    for driver in online_drivers:
        if not driver.current_location_lat or not driver.current_location_lng:
            continue
        
        # Calculate distance and ETA
        distance = haversine_distance(
            float(driver.current_location_lat),
            float(driver.current_location_lng),
            float(ride.pickup_location_lat),
            float(ride.pickup_location_lng)
        )
        
        eta = estimate_eta(distance, float(ride.traffic_score))
        
        # Calculate trip distance
        trip_distance = haversine_distance(
            float(ride.pickup_location_lat),
            float(ride.pickup_location_lng),
            float(ride.dropoff_location_lat),
            float(ride.dropoff_location_lng)
        )
        
        # Calculate fare
        estimated_fare = calculate_fare(
            trip_distance,
            float(ride.traffic_score),
            float(ride.demand_multiplier)
        )
        fare_per_km = estimated_fare / max(trip_distance, 0.1)
        
        # **ML-BASED ACCEPTANCE PREDICTION**
        try:
            acceptance_prob = predictor.predict(
                trip_distance_km=distance,
                trip_estimated_km=trip_distance,
                traffic_score=float(ride.traffic_score),
                fare_per_km=fare_per_km,
                demand_multiplier=float(ride.demand_multiplier),
                hour_of_day=current_hour,
                driver_fatigue_score=float(driver.fatigue_score),
                driver_acceptance_rate=float(driver.acceptance_rate),
                driver_earnings_last_hour=float(driver.earnings_last_hour),
                driver_trips_today=driver.total_trips,
                earnings_today=float(driver.earnings_today)
            )
            prediction_source = "ml" if predictor.model is not None else "heuristic"
        except Exception as e:
            logger.error(f"Error in ML prediction: {e}")
            # Fallback to simple heuristic
            acceptance_prob = 0.7 - min(distance * 0.02, 0.3)
            prediction_source = "error_fallback"
        
        # Calculate overall matching score
        score_data = calculate_overall_score(
            acceptance_prob=acceptance_prob,
            eta_minutes=eta,
            total_trips=driver.total_trips,
            earnings=float(driver.earnings_today),
            acceptance_weight=settings.ACCEPTANCE_WEIGHT,
            eta_weight=settings.ETA_WEIGHT,
            fairness_weight=settings.FAIRNESS_WEIGHT,
            avg_trips=avg_trips,
            avg_earnings=avg_earnings
        )
        
        driver_matches.append(DriverMatch(
            driver_id=driver.driver_id,
            driver_name=driver.name,
            distance_km=round(distance, 2),
            eta_minutes=eta,
            acceptance_probability=round(acceptance_prob, 4),
            overall_score=score_data["overall_score"],
            score_breakdown=score_data,
            prediction_source=prediction_source
        ))
    
    # Sort by overall score (descending)
    driver_matches.sort(key=lambda x: x.overall_score, reverse=True)
    
    # Return top N drivers
    top_matches = driver_matches[:max_drivers]
    
    logger.info(f"Found {len(top_matches)} drivers for ride {request.ride_id}")
    
    return MatchResponse(
        ride_id=request.ride_id,
        matched_drivers=top_matches
    )
