"""
Generate synthetic training data for ride denial prediction model

This script creates realistic training data based on driver and ride characteristics
to train the XGBoost model for predicting ride acceptance/denial.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys
import os

# Add backend to path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
sys.path.insert(0, backend_dir)

from app.db.session import SessionLocal
from app.models.driver import Driver
from app.models.ride import RideRequest
from app.utils.geo import haversine_distance

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Bangalore coordinates
BANGALORE_LAT_MIN, BANGALORE_LAT_MAX = 12.8, 13.2
BANGALORE_LNG_MIN, BANGALORE_LNG_MAX = 77.4, 77.8


def random_location():
    """Generate random Bangalore location"""
    lat = random.uniform(BANGALORE_LAT_MIN, BANGALORE_LAT_MAX)
    lng = random.uniform(BANGALORE_LNG_MIN, BANGALORE_LNG_MAX)
    return lat, lng


def calculate_features(driver_data, ride_data, current_time):
    """
    Calculate features for the ML model
    
    Features:
    - trip_distance_km: Distance from driver to pickup
    - trip_estimated_km: Total trip distance
    - traffic_score: 0-1 (congestion level)
    - fare_per_km: Estimated fare divided by distance
    - is_peak_hour: Boolean (7-10 AM, 5-9 PM)
    - hour_of_day: 0-23
    - driver_fatigue_score: 0-1
    - driver_acceptance_rate: Historical acceptance rate
    - driver_earnings_last_hour: Recent earnings
    - driver_trips_today: Number of trips completed today
    - earnings_velocity: Earnings per hour today
    - is_long_trip: Trip > 15km
    - demand_multiplier: Surge pricing factor
    """
    # Distance calculations
    driver_to_pickup = haversine_distance(
        driver_data['lat'], driver_data['lng'],
        ride_data['pickup_lat'], ride_data['pickup_lng']
    )
    
    trip_distance = haversine_distance(
        ride_data['pickup_lat'], ride_data['pickup_lng'],
        ride_data['dropoff_lat'], ride_data['dropoff_lng']
    )
    
    # Fare calculation
    base_fare = 30
    per_km_rate = 12
    estimated_fare = (base_fare + trip_distance * per_km_rate) * ride_data['demand_multiplier']
    fare_per_km = estimated_fare / max(trip_distance, 0.1)
    
    # Time features
    hour = current_time.hour
    is_peak_hour = (7 <= hour <= 10) or (17 <= hour <= 21)
    
    # Driver features
    trips_today = driver_data['trips_today']
    earnings_today = driver_data['earnings_today']
    hours_worked = max(current_time.hour - 6, 1)  # Assume started at 6 AM
    earnings_velocity = earnings_today / hours_worked
    
    features = {
        # Trip features
        'trip_distance_km': round(driver_to_pickup, 2),
        'trip_estimated_km': round(trip_distance, 2),
        'traffic_score': ride_data['traffic_score'],
        'fare_per_km': round(fare_per_km, 2),
        'is_long_trip': int(trip_distance > 15),
        'demand_multiplier': ride_data['demand_multiplier'],
        
        # Time features
        'is_peak_hour': int(is_peak_hour),
        'hour_of_day': hour,
        
        # Driver features
        'driver_fatigue_score': driver_data['fatigue_score'],
        'driver_acceptance_rate': driver_data['acceptance_rate'],
        'driver_earnings_last_hour': driver_data['earnings_last_hour'],
        'driver_trips_today': trips_today,
        'earnings_velocity': round(earnings_velocity, 2),
    }
    
    return features


def generate_acceptance_label(features):
    """
    Generate acceptance label based on features with realistic probabilities
    
    Factors that reduce acceptance:
    - Long distance to pickup
    - Low fare per km
    - High driver fatigue
    - High recent earnings (already earned enough)
    - Very long trips
    - Off-peak hours with low demand
    """
    # Base acceptance probability
    base_prob = 0.75
    
    # Distance penalty (farther = less likely)
    distance_penalty = min(features['trip_distance_km'] * 0.03, 0.3)
    
    # Fare attractiveness (low fare/km = less likely)
    fare_penalty = 0.2 if features['fare_per_km'] < 10 else 0
    
    # Fatigue penalty
    fatigue_penalty = features['driver_fatigue_score'] * 0.25
    
    # Earnings saturation (already earned a lot today)
    earnings_penalty = min(features['earnings_velocity'] / 100, 0.2)
    
    # Long trip penalty (drivers may avoid very long trips)
    long_trip_penalty = 0.15 if features['is_long_trip'] else 0
    
    # Peak hour bonus (higher acceptance during peak)
    peak_bonus = 0.1 if features['is_peak_hour'] else 0
    
    # High demand bonus
    demand_bonus = (features['demand_multiplier'] - 1) * 0.1
    
    # Calculate final probability
    acceptance_prob = base_prob - distance_penalty - fare_penalty - fatigue_penalty - earnings_penalty - long_trip_penalty + peak_bonus + demand_bonus
    
    # Clip to valid range
    acceptance_prob = np.clip(acceptance_prob, 0.05, 0.95)
    
    # Sample from Bernoulli distribution
    accepted = np.random.binomial(1, acceptance_prob)
    
    return accepted, acceptance_prob


def generate_training_data(num_samples=5000):
    """Generate synthetic training data"""
    print(f"Generating {num_samples} training samples...")
    
    data = []
    
    for i in range(num_samples):
        if i % 1000 == 0:
            print(f"  Generated {i}/{num_samples} samples...")
        
        # Random time (spread across working hours)
        hour = random.choice([7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22])
        current_time = datetime.now().replace(hour=hour, minute=random.randint(0, 59))
        
        # Generate driver data
        driver_data = {
            'lat': random.uniform(BANGALORE_LAT_MIN, BANGALORE_LAT_MAX),
            'lng': random.uniform(BANGALORE_LNG_MIN, BANGALORE_LNG_MAX),
            'fatigue_score': np.clip(np.random.normal(0.3, 0.2), 0, 1),
            'acceptance_rate': np.clip(np.random.normal(0.75, 0.15), 0.3, 0.98),
            'earnings_last_hour': np.random.exponential(80),
            'trips_today': np.random.poisson(10),
            'earnings_today': np.random.exponential(500),
        }
        
        # Generate ride data
        pickup_lat, pickup_lng = random_location()
        dropoff_lat, dropoff_lng = random_location()
        
        ride_data = {
            'pickup_lat': pickup_lat,
            'pickup_lng': pickup_lng,
            'dropoff_lat': dropoff_lat,
            'dropoff_lng': dropoff_lng,
            'traffic_score': np.clip(np.random.beta(2, 2), 0, 1),
            'demand_multiplier': np.random.choice([1.0, 1.2, 1.5, 1.8, 2.0], p=[0.5, 0.2, 0.15, 0.1, 0.05]),
        }
        
        # Calculate features
        features = calculate_features(driver_data, ride_data, current_time)
        
        # Generate label
        accepted, true_prob = generate_acceptance_label(features)
        
        # Combine features and label
        sample = {**features, 'accepted': accepted, 'true_acceptance_prob': round(true_prob, 4)}
        data.append(sample)
    
    print(f"✓ Generated {num_samples} samples")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(df)}")
    print(f"  Accepted: {df['accepted'].sum()} ({df['accepted'].mean()*100:.1f}%)")
    print(f"  Denied: {(1-df['accepted']).sum()} ({(1-df['accepted']).mean()*100:.1f}%)")
    print(f"\nFeature ranges:")
    print(df.describe())
    
    return df


def main():
    print("=" * 60)
    print(" Ride Denial Prediction - Training Data Generator")
    print("=" * 60)
    
    # Generate training data
    df = generate_training_data(num_samples=5000)
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), '..', 'processed', 'training_data.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved training data to: {output_path}")
    
    print("\n" + "=" * 60)
    print(" Training data generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
