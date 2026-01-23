from typing import Dict, Any


def calculate_acceptance_score(acceptance_probability: float) -> float:
    """
    Calculate acceptance score component
    Higher probability = higher score
    """
    return acceptance_probability


def calculate_eta_score(eta_minutes: int, max_eta: int = 30) -> float:
    """
    Calculate ETA score component
    Closer drivers score higher
    
    Args:
        eta_minutes: Estimated time of arrival in minutes
        max_eta: Maximum acceptable ETA
    
    Returns:
        Score between 0 and 1
    """
    if eta_minutes >= max_eta:
        return 0.0
    
    # Linear decay: closer is better
    return 1.0 - (eta_minutes / max_eta)


def calculate_fairness_score(
    total_trips_today: int,
    earnings_today: float,
    avg_trips_today: float = 10.0,
    avg_earnings_today: float = 500.0
) -> float:
    """
    Calculate fairness score to distribute rides more evenly
    Drivers with fewer trips/earnings get higher scores
    
    Args:
        total_trips_today: Number of trips completed today
        earnings_today: Total earnings today
        avg_trips_today: Average trips across all drivers
        avg_earnings_today: Average earnings across all drivers
    
    Returns:
        Score between 0 and 1
    """
    # Normalize trips and earnings
    trip_ratio = total_trips_today / max(avg_trips_today, 1)
    earnings_ratio = earnings_today / max(avg_earnings_today, 1)
    
    # Lower values get higher scores (inverse relationship)
    trip_score = max(0.0, 1.0 - trip_ratio)
    earnings_score = max(0.0, 1.0 - earnings_ratio)
    
    # Combined fairness score
    return (trip_score + earnings_score) / 2.0


def calculate_overall_score(
    acceptance_prob: float,
    eta_minutes: int,
    total_trips: int,
    earnings: float,
    acceptance_weight: float = 0.45,
    eta_weight: float = 0.35,
    fairness_weight: float = 0.20,
    avg_trips: float = 10.0,
    avg_earnings: float = 500.0
) -> Dict[str, Any]:
    """
    Calculate overall matching score for a driver
    
    Returns:
        Dictionary with overall score and component scores
    """
    acceptance_score = calculate_acceptance_score(acceptance_prob)
    eta_score = calculate_eta_score(eta_minutes)
    fairness_score = calculate_fairness_score(total_trips, earnings, avg_trips, avg_earnings)
    
    overall_score = (
        acceptance_weight * acceptance_score +
        eta_weight * eta_score +
        fairness_weight * fairness_score
    )
    
    return {
        "overall_score": round(overall_score, 4),
        "acceptance_score": round(acceptance_score, 4),
        "eta_score": round(eta_score, 4),
        "fairness_score": round(fairness_score, 4),
        "components": {
            "acceptance": {
                "score": round(acceptance_score, 4),
                "weight": acceptance_weight,
                "contribution": round(acceptance_weight * acceptance_score, 4)
            },
            "eta": {
                "score": round(eta_score, 4),
                "weight": eta_weight,
                "contribution": round(eta_weight * eta_score, 4)
            },
            "fairness": {
                "score": round(fairness_score, 4),
                "weight": fairness_weight,
                "contribution": round(fairness_weight * fairness_score, 4)
            }
        }
    }
