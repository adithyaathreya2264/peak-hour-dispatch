"""
Zone-based demand forecasting and heat map generation

This module handles geographic zone management, demand aggregation,
and prediction for visualizing hotspots on the heat map.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import numpy as np
from pydantic import BaseModel


# Define geographic zones for Bangalore
# Grid-based approach: divide city into 6x6 grid (36 zones)
BANGALORE_LAT_MIN, BANGALORE_LAT_MAX = 12.8, 13.2
BANGALORE_LNG_MIN, BANGALORE_LNG_MAX = 77.4, 77.8

GRID_SIZE = 6  # 6x6 grid
LAT_STEP = (BANGALORE_LAT_MAX - BANGALORE_LAT_MIN) / GRID_SIZE
LNG_STEP = (BANGALORE_LNG_MAX - BANGALORE_LNG_MIN) / GRID_SIZE


class Zone(BaseModel):
    """Geographic zone representation"""
    zone_id: str  # Format: "Z_<row>_<col>"
    center_lat: float
    center_lng: float
    bounds: Dict[str, float]  # north, south, east, west
    row: int
    col: int


class ZoneDemand(BaseModel):
    """Demand metrics for a zone at a specific time"""
    zone_id: str
    timestamp: datetime
    request_count: int
    driver_count: int
    demand_score: float  # Normalized demand metric (0-1)
    predicted_demand: float  # Forecasted demand for next period


def create_zones() -> List[Zone]:
    """
    Create grid of zones covering Bangalore
    Returns list of 36 zones (6x6 grid)
    """
    zones = []
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Calculate bounds
            south = BANGALORE_LAT_MIN + (row * LAT_STEP)
            north = south + LAT_STEP
            west = BANGALORE_LNG_MIN + (col * LNG_STEP)
            east = west + LNG_STEP
            
            # Center point
            center_lat = (south + north) / 2
            center_lng = (west + east) / 2
            
            zone = Zone(
                zone_id=f"Z_{row}_{col}",
                center_lat=center_lat,
                center_lng=center_lng,
                bounds={
                    "north": north,
                    "south": south,
                    "east": east,
                    "west": west
                },
                row=row,
                col=col
            )
            zones.append(zone)
    
    return zones


def get_zone_for_location(lat: float, lng: float) -> str:
    """
    Determine which zone a location belongs to
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        zone_id: String identifier like "Z_2_3"
    """
    if not (BANGALORE_LAT_MIN <= lat <= BANGALORE_LAT_MAX and 
            BANGALORE_LNG_MIN <= lng <= BANGALORE_LNG_MAX):
        return None
    
    row = int((lat - BANGALORE_LAT_MIN) / LAT_STEP)
    col = int((lng - BANGALORE_LNG_MIN) / LNG_STEP)
    
    # Clamp to valid range
    row = min(row, GRID_SIZE - 1)
    col = min(col, GRID_SIZE - 1)
    
    return f"Z_{row}_{col}"


def calculate_demand_score(request_count: int, driver_count: int) -> float:
    """
    Calculate normalized demand score for a zone
    
    High demand score = many requests, few drivers
    Low demand score = few requests, many drivers
    
    Returns:
        float: 0-1 score (0=low demand, 1=high demand)
    """
    if driver_count == 0:
        # No drivers available
        return min(1.0, request_count / 10)  # Cap at 1.0
    
    # Demand/supply ratio
    ratio = request_count / driver_count
    
    # Normalize to 0-1 range (assume ratio of 2.0 = very high demand)
    score = min(1.0, ratio / 2.0)
    
    return score


def simple_demand_forecast(
    historical_requests: List[int],
    hour_of_day: int,
    day_of_week: int
) -> float:
    """
    Simple heuristic-based demand forecasting
    
    In production, this would use Prophet or SARIMA
    For MVP, use pattern matching:
    - Peak hours (7-10 AM, 5-9 PM): Higher demand
    - Weekends: Different patterns
    - Historical average for this hour
    
    Args:
        historical_requests: List of request counts from past periods
        hour_of_day: Current hour (0-23)
        day_of_week: Day of week (0=Monday, 6=Sunday)
    
    Returns:
        Predicted request count for next period
    """
    # Base prediction from historical average
    if len(historical_requests) > 0:
        base_prediction = np.mean(historical_requests[-24:])  # Last 24 hours
    else:
        base_prediction = 5.0
    
    # Peak hour multipliers
    is_morning_peak = 7 <= hour_of_day <= 10
    is_evening_peak = 17 <= hour_of_day <= 21
    is_weekend = day_of_week >= 5
    
    multiplier = 1.0
    
    if is_morning_peak:
        multiplier = 1.8
    elif is_evening_peak:
        multiplier = 2.2  # Evening peak stronger
    elif is_weekend:
        multiplier = 0.8  # Lower weekday commute demand
    
    predicted = base_prediction * multiplier
    
    # Add some randomness
    predicted += np.random.normal(0, predicted * 0.1)
    
    return max(0, predicted)


def aggregate_zone_demand(
    zones: List[Zone],
    rides: List[Dict],
    drivers: List[Dict],
    current_time: datetime
) -> List[ZoneDemand]:
    """
    Aggregate current demand metrics by zone
    
    Args:
        zones: List of defined zones
        rides: List of ride requests (dicts with pickup_lat, pickup_lng)
        drivers: List of drivers (dicts with lat, lng, online_status)
        current_time: Current timestamp
    
    Returns:
        List of ZoneDemand objects with current metrics
    """
    # Initialize counters for each zone
    zone_requests = {zone.zone_id: 0 for zone in zones}
    zone_drivers = {zone.zone_id: 0 for zone in zones}
    
    # Count requests per zone
    for ride in rides:
        zone_id = get_zone_for_location(ride['pickup_lat'], ride['pickup_lng'])
        if zone_id:
            zone_requests[zone_id] += 1
    
    # Count online drivers per zone
    for driver in drivers:
        if driver.get('online_status'):
            zone_id = get_zone_for_location(driver['lat'], driver['lng'])
            if zone_id:
                zone_drivers[zone_id] += 1
    
    # Calculate metrics for each zone
    zone_demands = []
    
    for zone in zones:
        request_count = zone_requests[zone.zone_id]
        driver_count = zone_drivers[zone.zone_id]
        demand_score = calculate_demand_score(request_count, driver_count)
        
        # Simple forecast (in production, use trained model)
        hour = current_time.hour
        day = current_time.weekday()
        predicted = simple_demand_forecast([request_count], hour, day)
        
        zone_demand = ZoneDemand(
            zone_id=zone.zone_id,
            timestamp=current_time,
            request_count=request_count,
            driver_count=driver_count,
            demand_score=demand_score,
            predicted_demand=predicted
        )
        zone_demands.append(zone_demand)
    
    return zone_demands


# Global zones cache
_zones_cache = None


def get_zones() -> List[Zone]:
    """Get or create zones (cached)"""
    global _zones_cache
    if _zones_cache is None:
        _zones_cache = create_zones()
    return _zones_cache
