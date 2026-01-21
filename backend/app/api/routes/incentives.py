from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, UUID4
from app.db.session import get_db
from app.models.ride import Incentive
from app.models.driver import Driver
from app.schemas.ride import IncentiveCreate, IncentiveResponse
from app.core.config import settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class IncentiveDecision(BaseModel):
    driver_id: UUID4
    ride_id: UUID4
    acceptance_probability: float
    trip_distance_km: Optional[float] = None
    demand_multiplier: Optional[float] = 1.0


class IncentiveRecommendation(BaseModel):
    should_offer: bool
    incentive_type: str = None
    amount: float = 0.0
    reason: str
    confidence: float = 0.0  # How confident we are in this decision


class StreakInfo(BaseModel):
    current_streak: int
    rides_until_bonus: int
    bonus_amount: float


def calculate_incentive_amount(acceptance_prob: float, base_amount: float = 20.0) -> float:
    """
    Calculate incentive amount based on acceptance probability
    Lower probability = higher incentive needed
    """
    if acceptance_prob < 0.25:
        return base_amount * 2.0  # ₹40 for very low probability
    elif acceptance_prob < 0.35:
        return base_amount * 1.5  # ₹30 for low probability
    else:
        return base_amount  # ₹20 for medium-low probability


def check_streak_eligibility(driver_id: UUID4, db: Session) -> StreakInfo:
    """
    Check if driver is eligible for streak rewards
    Streak reward: Complete 3 rides in a row → ₹50 bonus
    """
    # Get driver's recent completed trips
    # For MVP, we'll simulate this - in production, query trip_outcomes
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    
    if not driver:
        return StreakInfo(current_streak=0, rides_until_bonus=3, bonus_amount=0)
    
    # Simulate streak tracking (would be stored in DB in production)
    # For demo, use trips_today as a proxy
    trips_today = driver.total_trips
    current_streak = trips_today % 3
    rides_until_bonus = 3 - current_streak
    bonus_amount = 50.0 if rides_until_bonus == 1 else 0.0
    
    return StreakInfo(
        current_streak=current_streak,
        rides_until_bonus=rides_until_bonus,
        bonus_amount=bonus_amount
    )


@router.post("/decide", response_model=IncentiveRecommendation)
async def decide_incentive(decision_request: IncentiveDecision, db: Session = Depends(get_db)):
    """
    ML-aware multi-tier incentive decision engine
    
    Decision Logic:
    1. Very Low (<25%): Offer large incentive (₹40)
    2. Low (25-35%): Offer medium incentive (₹30)
    3. Medium (35-45%): Offer small incentive (₹20)
    4. High (>45%): Consider streak bonus or no incentive
    5. Peak hours + low supply: Boost incentive by 1.2x
    """
    acceptance_prob = decision_request.acceptance_probability
    demand_mult = decision_request.demand_multiplier or 1.0
    
    # Get streak info
    streak_info = check_streak_eligibility(decision_request.driver_id, db)
    
    # Decision threshold (configurable)
    INCENTIVE_THRESHOLD = settings.INCENTIVE_ACCEPTANCE_THRESHOLD  # 0.4
    
    # High acceptance probability - minimal/no incentive needed
    if acceptance_prob >= INCENTIVE_THRESHOLD:
        # Check if streak bonus applies
        if streak_info.rides_until_bonus == 1:
            return IncentiveRecommendation(
                should_offer=True,
                incentive_type="streak_bonus",
                amount=streak_info.bonus_amount,
                reason=f"Streak bonus: Complete 1 more ride to earn ₹{streak_info.bonus_amount}",
                confidence=0.9
            )
        else:
            return IncentiveRecommendation(
                should_offer=False,
                reason=f"High acceptance probability ({acceptance_prob:.2%}), no incentive needed",
                confidence=0.8
            )
    
    # Low to medium acceptance - offer tiered incentive
    base_amount = calculate_incentive_amount(acceptance_prob)
    
    # Apply surge multiplier if high demand
    if demand_mult >= 2.0:
        base_amount *= 1.2  # 20% boost during surge
        surge_note = " (surge bonus applied)"
    elif demand_mult >= 1.5:
        base_amount *= 1.1  # 10% boost during medium surge
        surge_note = " (medium surge bonus)"
    else:
        surge_note = ""
    
    # Determine confidence based on how far we are from threshold
    distance_from_threshold = INCENTIVE_THRESHOLD - acceptance_prob
    confidence = min(0.95, 0.5 + (distance_from_threshold * 2))
    
    return IncentiveRecommendation(
        should_offer=True,
        incentive_type="cash_bonus",
        amount=round(base_amount, 2),
        reason=f"Low acceptance ({acceptance_prob:.2%}) - offering ₹{base_amount:.0f} to boost" + surge_note,
        confidence=confidence
    )


@router.get("/streak/{driver_id}", response_model=StreakInfo)
async def get_driver_streak(driver_id: UUID4, db: Session = Depends(get_db)):
    """Get driver's current streak information"""
    return check_streak_eligibility(driver_id, db)



@router.post("/", response_model=IncentiveResponse, status_code=201)
async def create_incentive(incentive: IncentiveCreate, db: Session = Depends(get_db)):
    """Create and offer an incentive"""
    try:
        db_incentive = Incentive(**incentive.dict())
        db.add(db_incentive)
        db.commit()
        db.refresh(db_incentive)
        
        logger.info(f"Created incentive: {db_incentive.incentive_id} - {incentive.incentive_type} ₹{incentive.amount}")
        return db_incentive
    
    except Exception as e:
        logger.error(f"Error creating incentive: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/driver/{driver_id}", response_model=List[IncentiveResponse])
async def get_driver_incentives(
    driver_id: str,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """Get incentives for a specific driver"""
    query = db.query(Incentive).filter(Incentive.driver_id == driver_id)
    
    if status_filter:
        query = query.filter(Incentive.status == status_filter)
    
    incentives = query.all()
    return incentives


@router.patch("/{incentive_id}/accept")
async def accept_incentive(incentive_id: str, db: Session = Depends(get_db)):
    """Mark incentive as accepted"""
    incentive = db.query(Incentive).filter(Incentive.incentive_id == incentive_id).first()
    if not incentive:
        raise HTTPException(status_code=404, detail="Incentive not found")
    
    incentive.status = "accepted"
    db.commit()
    
    logger.info(f"Incentive accepted: {incentive_id}")
    return {"status": "accepted"}
