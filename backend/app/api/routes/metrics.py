from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from pydantic import BaseModel
from app.db.session import get_db
from app.models.driver import Driver
from app.models.ride import RideRequest, TripOutcome, Incentive
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class SystemMetrics(BaseModel):
    total_rides: int
    pending_rides: int
    completed_rides: int
    total_drivers: int
    online_drivers: int
    avg_acceptance_rate: float
    total_incentives_offered: int
    total_incentive_cost: float
    avg_wait_time_minutes: float


@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics(db: Session = Depends(get_db)):
    """Get overall system metrics"""
    
    # Ride metrics
    total_rides = db.query(func.count(RideRequest.ride_id)).scalar()
    pending_rides = db.query(func.count(RideRequest.ride_id)).filter(
        RideRequest.status == 'pending'
    ).scalar()
    completed_rides = db.query(func.count(RideRequest.ride_id)).filter(
        RideRequest.status == 'completed'
    ).scalar()
    
    # Driver metrics
    total_drivers = db.query(func.count(Driver.driver_id)).scalar()
    online_drivers = db.query(func.count(Driver.driver_id)).filter(
        Driver.online_status == True
    ).scalar()
    
    avg_acceptance = db.query(func.avg(Driver.acceptance_rate)).scalar() or 0.0
    
    # Incentive metrics
    total_incentives = db.query(func.count(Incentive.incentive_id)).scalar()
    total_cost = db.query(func.sum(Incentive.amount)).scalar() or 0.0
    
    # Mock wait time (in Phase 2+, calculate from actual data)
    avg_wait_time = 5.5
    
    return SystemMetrics(
        total_rides=total_rides or 0,
        pending_rides=pending_rides or 0,
        completed_rides=completed_rides or 0,
        total_drivers=total_drivers or 0,
        online_drivers=online_drivers or 0,
        avg_acceptance_rate=round(float(avg_acceptance), 2),
        total_incentives_offered=total_incentives or 0,
        total_incentive_cost=round(float(total_cost), 2),
        avg_wait_time_minutes=avg_wait_time
    )


@router.get("/performance")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Get detailed performance analytics"""
    
    # Acceptance rates
    total_outcomes = db.query(func.count(TripOutcome.outcome_id)).scalar() or 1
    accepted_outcomes = db.query(func.count(TripOutcome.outcome_id)).filter(
        TripOutcome.accepted == True
    ).scalar() or 0
    
    acceptance_rate = (accepted_outcomes / total_outcomes) * 100 if total_outcomes > 0 else 0
    
    # Incentive effectiveness
    outcomes_with_incentive = db.query(func.count(TripOutcome.outcome_id)).filter(
        TripOutcome.incentive_given == True
    ).scalar() or 1
    
    accepted_with_incentive = db.query(func.count(TripOutcome.outcome_id)).filter(
        TripOutcome.incentive_given == True,
        TripOutcome.accepted == True
    ).scalar() or 0
    
    incentive_effectiveness = (accepted_with_incentive / outcomes_with_incentive) * 100 if outcomes_with_incentive > 0 else 0
    
    return {
        "overall_acceptance_rate": round(acceptance_rate, 2),
        "incentive_effectiveness_rate": round(incentive_effectiveness, 2),
        "total_trip_outcomes": total_outcomes,
        "accepted_trips": accepted_outcomes,
        "rejected_trips": total_outcomes - accepted_outcomes,
        "outcomes_with_incentive": outcomes_with_incentive,
        "accepted_with_incentive": accepted_with_incentive
    }
