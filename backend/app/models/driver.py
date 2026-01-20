from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.session import Base


class Driver(Base):
    __tablename__ = "drivers"
    
    driver_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    current_location_lat = Column(DECIMAL(10, 8))
    current_location_lng = Column(DECIMAL(11, 8))
    online_status = Column(Boolean, default=False)
    acceptance_rate = Column(DECIMAL(5, 2), default=0.0)
    total_trips = Column(Integer, default=0)
    earnings_today = Column(DECIMAL(10, 2), default=0.0)
    earnings_last_hour = Column(DECIMAL(10, 2), default=0.0)
    fatigue_score = Column(DECIMAL(3, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Driver {self.name} ({self.driver_id})>"
