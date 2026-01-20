from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 6050
    API_RELOAD: bool = True
    
    # Database - Will be loaded from .env
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_RIDE_REQUESTS_TOPIC: str = "ride-requests"
    KAFKA_DRIVER_UPDATES_TOPIC: str = "driver-updates"
    KAFKA_INCENTIVES_TOPIC: str = "incentives"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    
    # ML Models
    MODEL_PATH: str = "backend/app/ml/models/"
    DENIAL_MODEL_NAME: str = "denial_model.pkl"
    DEMAND_MODEL_NAME: str = "demand_model.pkl"
    
    # Mapbox
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Matching Engine Parameters
    ACCEPTANCE_WEIGHT: float = 0.45
    ETA_WEIGHT: float = 0.35
    FAIRNESS_WEIGHT: float = 0.20
    
    # Incentive Thresholds
    INCENTIVE_ACCEPTANCE_THRESHOLD: float = 0.4
    BASE_CASH_INCENTIVE: float = 20.0
    STREAK_RIDE_COUNT: int = 3
    STREAK_BONUS: float = 50.0
    
    class Config:
        # Look for .env in project root
        from pathlib import Path
        env_file = str(Path(__file__).parent.parent.parent.parent / ".env")
        case_sensitive = True


settings = Settings()
