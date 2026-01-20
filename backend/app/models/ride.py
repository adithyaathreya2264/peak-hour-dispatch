from sqlalchemy import Column, String, Float, Integer, DateTime, DECIMAL, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.session import Base


class RideRequest(Base):
    __tablename__ = "ride_requests"
    
    ride_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rider_name = Column(String(255))
    pickup_location_lat = Column(DECIMAL(10, 8), nullable=False)
    pickup_location_lng = Column(DECIMAL(11, 8), nullable=False)
    dropoff_location_lat = Column(DECIMAL(10, 8), nullable=False)
    dropoff_location_lng = Column(DECIMAL(11, 8), nullable=False)
    request_time = Column(DateTime, default=datetime.utcnow)
    estimated_fare = Column(DECIMAL(10, 2))
    estimated_distance = Column(DECIMAL(10, 2))
    traffic_score = Column(DECIMAL(3, 2), default=0.0)
    demand_multiplier = Column(DECIMAL(3, 2), default=1.0)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RideRequest {self.ride_id} - {self.status}>"


class TripOutcome(Base):
    __tablename__ = "trip_outcomes"
    
    outcome_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id = Column(UUID(as_uuid=True), ForeignKey('ride_requests.ride_id'))
    driver_id = Column(UUID(as_uuid=True), ForeignKey('drivers.driver_id'))
    acceptance_probability = Column(DECIMAL(5, 4))
    accepted = Column(Boolean, default=False)
    completed = Column(Boolean, default=False)
    incentive_given = Column(Boolean, default=False)
    incentive_type = Column(String(50))
    incentive_amount = Column(DECIMAL(10, 2), default=0.0)
    rejection_reason = Column(String(255))
    final_fare = Column(DECIMAL(10, 2))
    trip_duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TripOutcome {self.outcome_id} - Accepted: {self.accepted}>"


class Incentive(Base):
    __tablename__ = "incentives"
    
    incentive_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey('drivers.driver_id'))
    ride_id = Column(UUID(as_uuid=True), ForeignKey('ride_requests.ride_id'))
    incentive_type = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    conditions = Column(String)  # JSON string
    status = Column(String(50), default='offered')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Incentive {self.incentive_id} - {self.incentive_type}>"
