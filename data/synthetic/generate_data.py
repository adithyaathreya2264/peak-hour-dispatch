"""
Script to generate mock data for drivers and riders
Run this after database initialization
"""
import random
import sys
import os
from decimal import Decimal

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
sys.path.insert(0, backend_dir)

from app.db.session import SessionLocal, engine
from app.db.session import Base
from app.models.driver import Driver
from app.models.ride import RideRequest, TripOutcome, Incentive


# Bangalore coordinates (rough bounds)
BANGALORE_LAT_MIN, BANGALORE_LAT_MAX = 12.8, 13.2
BANGALORE_LNG_MIN, BANGALORE_LNG_MAX = 77.4, 77.8

DRIVER_NAMES = [
    "Rajesh Kumar", "Suresh Reddy", "Amit Sharma", "Vijay Singh", "Ramesh Patil",
    "Prakash Rao", "Manoj Gupta", "Santosh Kumar", "Anil Verma", "Ravi Shankar",
    "Dinesh Yadav", "Ganesh Patel", "Rahul Mehta", "Ashok Jain", "Naveen Kumar",
    "Rakesh Singh", "Sanjay Mishra", "Pankaj Sharma", "Deepak Tiwari", "Vinod Kumar"
]

RIDER_NAMES = [
    "Priya Sharma", "Anita Reddy", "Sneha Patel", "Kavya Iyer", "Divya Nair",
    "Meera Gupta", "Pooja Kumar", "Swati Verma", "Neha Singh", "Anjali Rao"
]


def random_location():
    """Generate random Bangalore location"""
    lat = random.uniform(BANGALORE_LAT_MIN, BANGALORE_LAT_MAX)
    lng = random.uniform(BANGALORE_LNG_MIN, BANGALORE_LNG_MAX)
    return Decimal(str(round(lat, 6))), Decimal(str(round(lng, 6)))


def generate_drivers(session, count=20):
    """Generate mock driver data"""
    print(f"Generating {count} drivers...")
    
    for i, name in enumerate(DRIVER_NAMES[:count]):
        lat, lng = random_location()
        
        driver = Driver(
            name=name,
            phone=f"+91{random.randint(7000000000, 9999999999)}",
            current_location_lat=lat,
            current_location_lng=lng,
            online_status=random.choice([True, True, True, False]),  # 75% online
            acceptance_rate=Decimal(str(round(random.uniform(0.6, 0.95), 2))),
            total_trips=random.randint(50, 500),
            earnings_today=Decimal(str(round(random.uniform(100, 800), 2))),
            earnings_last_hour=Decimal(str(round(random.uniform(0, 150), 2))),
            fatigue_score=Decimal(str(round(random.uniform(0.0, 0.7), 2)))
        )
        session.add(driver)
    
    session.commit()
    print(f"✓ Created {count} drivers")


def generate_ride_requests(session, count=10):
    """Generate mock ride requests"""
    print(f"Generating {count} ride requests...")
    
    for i in range(count):
        pickup_lat, pickup_lng = random_location()
        dropoff_lat, dropoff_lng = random_location()
        
        # Calculate rough distance for fare estimation
        distance = abs(float(pickup_lat - dropoff_lat)) + abs(float(pickup_lng - dropoff_lng))
        distance_km = distance * 111  # Rough conversion
        
        base_fare = 30
        fare = Decimal(str(round(base_fare + (distance_km * 12), 2)))
        
        ride = RideRequest(
            rider_name=random.choice(RIDER_NAMES),
            pickup_location_lat=pickup_lat,
            pickup_location_lng=pickup_lng,
            dropoff_location_lat=dropoff_lat,
            dropoff_location_lng=dropoff_lng,
            estimated_fare=fare,
            estimated_distance=Decimal(str(round(distance_km, 2))),
            traffic_score=Decimal(str(round(random.uniform(0.2, 0.8), 2))),
            demand_multiplier=Decimal(str(round(random.uniform(1.0, 2.0), 2))),
            status=random.choice(['pending', 'pending', 'pending', 'assigned', 'completed'])
        )
        session.add(ride)
    
    session.commit()
    print(f"✓ Created {count} ride requests")


def init_database():
    """Initialize database with schema"""
    print("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database schema created")


def main():
    print("=" * 60)
    print(" Peak Hour Dispatch AI - Mock Data Generator")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Create session
    session = SessionLocal()
    
    try:
        # Check if data already exists
        existing_drivers = session.query(Driver).count()
        if existing_drivers > 0:
            print(f"\n⚠️  Database already has {existing_drivers} drivers")
            response = input("Do you want to add more data? (y/n): ")
            if response.lower() != 'y':
                print("Exiting...")
                return
        
        # Generate data
        generate_drivers(session, count=20)
        generate_ride_requests(session, count=10)
        
        print("\n" + "=" * 60)
        print(" ✓ Mock data generation complete!")
        print("=" * 60)
        
        # Show summary
        total_drivers = session.query(Driver).count()
        online_drivers = session.query(Driver).filter(Driver.online_status == True).count()
        total_rides = session.query(RideRequest).count()
        
        print(f"\nSummary:")
        print(f"  Total Drivers: {total_drivers}")
        print(f"  Online Drivers: {online_drivers}")
        print(f"  Total Ride Requests: {total_rides}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
    
    finally:
        session.close()


if __name__ == "__main__":
    main()
