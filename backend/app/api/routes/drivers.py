from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse, DriverLocation
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    """Create a new driver"""
    try:
        db_driver = Driver(**driver.dict())
        db.add(db_driver)
        db.commit()
        db.refresh(db_driver)
        logger.info(f"Created driver: {db_driver.driver_id}")
        return db_driver
    except Exception as e:
        logger.error(f"Error creating driver: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DriverResponse])
async def get_drivers(
    online_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all drivers"""
    query = db.query(Driver)
    if online_only:
        query = query.filter(Driver.online_status == True)
    
    drivers = query.offset(skip).limit(limit).all()
    return drivers


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: str, db: Session = Depends(get_db)):
    """Get a specific driver by ID"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.patch("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: str,
    driver_update: DriverUpdate,
    db: Session = Depends(get_db)
):
    """Update driver information"""
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    update_data = driver_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(driver, field, value)
    
    db.commit()
    db.refresh(driver)
    logger.info(f"Updated driver: {driver_id}")
    return driver


@router.get("/online/locations", response_model=List[DriverLocation])
async def get_online_driver_locations(db: Session = Depends(get_db)):
    """Get locations of all online drivers"""
    drivers = db.query(Driver).filter(Driver.online_status == True).all()
    
    return [
        DriverLocation(
            driver_id=driver.driver_id,
            latitude=float(driver.current_location_lat or 0),
            longitude=float(driver.current_location_lng or 0),
            online_status=driver.online_status
        )
        for driver in drivers
        if driver.current_location_lat and driver.current_location_lng
    ]
