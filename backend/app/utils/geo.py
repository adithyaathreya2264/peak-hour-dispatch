from math import radians, sin, cos, sqrt, atan2
from typing import Tuple


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return r * c


def estimate_eta(distance_km: float, traffic_score: float = 0.5) -> int:
    """
    Estimate ETA in minutes based on distance and traffic
    
    Args:
        distance_km: Distance in kilometers
        traffic_score: Traffic score between 0 (no traffic) and 1 (heavy traffic)
    
    Returns:
        Estimated time in minutes
    """
    # Base speed: 30 km/h in moderate traffic
    base_speed_kmh = 30
    
    # Adjust speed based on traffic (lower speed in heavy traffic)
    speed_kmh = base_speed_kmh * (1 - traffic_score * 0.5)
    
    # Calculate time in minutes
    eta_minutes = (distance_km / speed_kmh) * 60
    
    return int(eta_minutes)


def calculate_fare(
    distance_km: float,
    traffic_score: float = 0.5,
    demand_multiplier: float = 1.0,
    base_fare: float = 30.0,
    per_km_rate: float = 12.0
) -> float:
    """
    Calculate estimated fare for a ride
    
    Args:
        distance_km: Distance in kilometers
        traffic_score: Traffic score (0-1)
        demand_multiplier: Surge pricing multiplier
        base_fare: Base fare in rupees
        per_km_rate: Rate per kilometer in rupees
    
    Returns:
        Estimated fare in rupees
    """
    # Base calculation
    fare = base_fare + (distance_km * per_km_rate)
    
    # Apply demand multiplier
    fare *= demand_multiplier
    
    # Add traffic surcharge (up to 20% extra)
    traffic_surcharge = fare * traffic_score * 0.2
    fare += traffic_surcharge
    
    return round(fare, 2)


def is_within_zone(
    lat: float,
    lon: float,
    zone_center_lat: float,
    zone_center_lon: float,
    radius_km: float
) -> bool:
    """
    Check if a point is within a circular zone
    
    Args:
        lat, lon: Point coordinates
        zone_center_lat, zone_center_lon: Zone center coordinates
        radius_km: Zone radius in kilometers
    
    Returns:
        True if point is within zone
    """
    distance = haversine_distance(lat, lon, zone_center_lat, zone_center_lon)
    return distance <= radius_km
