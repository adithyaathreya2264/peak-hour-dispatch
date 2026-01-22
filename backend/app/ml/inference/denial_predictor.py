"""
Ride Denial Prediction - ML Inference Service

Loads the trained XGBoost model and provides prediction functionality
for real-time ride acceptance probability estimation.
"""
import joblib
import numpy as np
import os
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class DenialPredictor:
    """ML-based ride acceptance/denial predictor"""
    
    def __init__(self, model_path: str = None):
        """Initialize the predictor and load the model"""
        if model_path is None:
            # Default model path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, '..', 'models', 'denial_model.pkl')
        
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk"""
        try:
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found at {self.model_path}. Using heuristic fallback.")
                return
            
            self.model = joblib.load(self.model_path)
            
            # Load feature names
            feature_names_path = os.path.join(os.path.dirname(self.model_path), 'feature_names.txt')
            if os.path.exists(feature_names_path):
                with open(feature_names_path, 'r') as f:
                    self.feature_names = [line.strip() for line in f.readlines()]
            
            logger.info(f"✓ Loaded ML model from {self.model_path}")
            logger.info(f"  Features: {len(self.feature_names) if self.feature_names else 'unknown'}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def prepare_features(
        self,
        trip_distance_km: float,
        trip_estimated_km: float,
        traffic_score: float,
        fare_per_km: float,
        is_long_trip: bool,
        demand_multiplier: float,
        is_peak_hour: bool,
        hour_of_day: int,
        driver_fatigue_score: float,
        driver_acceptance_rate: float,
        driver_earnings_last_hour: float,
        driver_trips_today: int,
        earnings_velocity: float
    ) -> np.ndarray:
        """
        Prepare features in the correct order for model prediction
        
        Features must match training data order:
        1. trip_distance_km
        2. trip_estimated_km
        3. traffic_score
        4. fare_per_km
        5. is_long_trip
        6. demand_multiplier
        7. is_peak_hour
        8. hour_of_day
        9. driver_fatigue_score
        10. driver_acceptance_rate
        11. driver_earnings_last_hour
        12. driver_trips_today
        13. earnings_velocity
        """
        features = np.array([[
            trip_distance_km,
            trip_estimated_km,
            traffic_score,
            fare_per_km,
            int(is_long_trip),
            demand_multiplier,
            int(is_peak_hour),
            hour_of_day,
            driver_fatigue_score,
            driver_acceptance_rate,
            driver_earnings_last_hour,
            driver_trips_today,
            earnings_velocity
        ]])
        
        return features
    
    def predict(
        self,
        trip_distance_km: float,
        trip_estimated_km: float,
        traffic_score: float,
        fare_per_km: float,
        demand_multiplier: float,
        hour_of_day: int,
        driver_fatigue_score: float,
        driver_acceptance_rate: float,
        driver_earnings_last_hour: float,
        driver_trips_today: int,
        earnings_today: float
    ) -> float:
        """
        Predict acceptance probability
        
        Returns:
            float: Probability of acceptance (0-1)
        """
        # Calculate derived features
        is_long_trip = trip_estimated_km > 15
        is_peak_hour = (7 <= hour_of_day <= 10) or (17 <= hour_of_day <= 21)
        
        # Calculate earnings velocity
        hours_worked = max(hour_of_day - 6, 1)  # Assume started at 6 AM
        earnings_velocity = earnings_today / hours_worked
        
        # If model is not loaded, use heuristic fallback
        if self.model is None:
            return self._heuristic_prediction(
                trip_distance_km, traffic_score, driver_fatigue_score,
                earnings_velocity, is_peak_hour, demand_multiplier
            )
        
        # Prepare features
        features = self.prepare_features(
            trip_distance_km=trip_distance_km,
            trip_estimated_km=trip_estimated_km,
            traffic_score=traffic_score,
            fare_per_km=fare_per_km,
            is_long_trip=is_long_trip,
            demand_multiplier=demand_multiplier,
            is_peak_hour=is_peak_hour,
            hour_of_day=hour_of_day,
            driver_fatigue_score=driver_fatigue_score,
            driver_acceptance_rate=driver_acceptance_rate,
            driver_earnings_last_hour=driver_earnings_last_hour,
            driver_trips_today=driver_trips_today,
            earnings_velocity=earnings_velocity
        )
        
        # Get prediction
        try:
            probability = self.model.predict_proba(features)[0][1]  # Probability of class 1 (acceptance)
            return float(probability)
        
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            # Fallback to heuristic
            return self._heuristic_prediction(
                trip_distance_km, traffic_score, driver_fatigue_score,
                earnings_velocity, is_peak_hour, demand_multiplier
            )
    
    def _heuristic_prediction(
        self,
        trip_distance_km: float,
        traffic_score: float,
        driver_fatigue_score: float,
        earnings_velocity: float,
        is_peak_hour: bool,
        demand_multiplier: float
    ) -> float:
        """
        Fallback heuristic prediction when ML model is not available
        
        This is the same logic used in the current matching.py
        """
        base_prob = 0.7
        distance_penalty = min(trip_distance_km * 0.02, 0.3)
        fatigue_penalty = driver_fatigue_score * 0.2
        earnings_factor = min(earnings_velocity / 100, 0.2)
        peak_bonus = 0.1 if is_peak_hour else 0
        demand_bonus = (demand_multiplier - 1) * 0.1
        
        acceptance_prob = base_prob - distance_penalty - fatigue_penalty - earnings_factor + peak_bonus + demand_bonus
        acceptance_prob = np.clip(acceptance_prob, 0.1, 0.95)
        
        # Add some randomness
        acceptance_prob += np.random.uniform(-0.05, 0.05)
        acceptance_prob = np.clip(acceptance_prob, 0.1, 0.95)
        
        return float(acceptance_prob)


# Global predictor instance (singleton)
_predictor_instance = None


def get_predictor() -> DenialPredictor:
    """Get or create the global predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DenialPredictor()
    return _predictor_instance
