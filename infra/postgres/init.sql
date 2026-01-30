-- Initialize database schema for Peak Hour Dispatch AI

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Driver table
CREATE TABLE IF NOT EXISTS drivers (
    driver_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    current_location_lat DECIMAL(10, 8),
    current_location_lng DECIMAL(11, 8),
    online_status BOOLEAN DEFAULT false,
    acceptance_rate DECIMAL(5, 2) DEFAULT 0.0,
    total_trips INTEGER DEFAULT 0,
    earnings_today DECIMAL(10, 2) DEFAULT 0.0,
    earnings_last_hour DECIMAL(10, 2) DEFAULT 0.0,
    fatigue_score DECIMAL(3, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ride request table
CREATE TABLE IF NOT EXISTS ride_requests (
    ride_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rider_name VARCHAR(255),
    pickup_location_lat DECIMAL(10, 8) NOT NULL,
    pickup_location_lng DECIMAL(11, 8) NOT NULL,
    dropoff_location_lat DECIMAL(10, 8) NOT NULL,
    dropoff_location_lng DECIMAL(11, 8) NOT NULL,
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_fare DECIMAL(10, 2),
    estimated_distance DECIMAL(10, 2),
    traffic_score DECIMAL(3, 2) DEFAULT 0.0,
    demand_multiplier DECIMAL(3, 2) DEFAULT 1.0,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trip outcome table
CREATE TABLE IF NOT EXISTS trip_outcomes (
    outcome_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ride_id UUID REFERENCES ride_requests(ride_id),
    driver_id UUID REFERENCES drivers(driver_id),
    acceptance_probability DECIMAL(5, 4),
    accepted BOOLEAN DEFAULT false,
    completed BOOLEAN DEFAULT false,
    incentive_given BOOLEAN DEFAULT false,
    incentive_type VARCHAR(50),
    incentive_amount DECIMAL(10, 2) DEFAULT 0.0,
    rejection_reason VARCHAR(255),
    final_fare DECIMAL(10, 2),
    trip_duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Incentives table
CREATE TABLE IF NOT EXISTS incentives (
    incentive_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id UUID REFERENCES drivers(driver_id),
    ride_id UUID REFERENCES ride_requests(ride_id),
    incentive_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    conditions JSONB,
    status VARCHAR(50) DEFAULT 'offered',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Demand zones table
CREATE TABLE IF NOT EXISTS demand_zones (
    zone_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zone_name VARCHAR(255) NOT NULL,
    center_lat DECIMAL(10, 8) NOT NULL,
    center_lng DECIMAL(11, 8) NOT NULL,
    radius_km DECIMAL(5, 2) NOT NULL,
    demand_score DECIMAL(5, 2) DEFAULT 0.0,
    driver_count INTEGER DEFAULT 0,
    active_requests INTEGER DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_drivers_location ON drivers(current_location_lat, current_location_lng);
CREATE INDEX idx_drivers_online ON drivers(online_status);
CREATE INDEX idx_ride_requests_status ON ride_requests(status);
CREATE INDEX idx_ride_requests_time ON ride_requests(request_time);
CREATE INDEX idx_trip_outcomes_driver ON trip_outcomes(driver_id);
CREATE INDEX idx_trip_outcomes_ride ON trip_outcomes(ride_id);
CREATE INDEX idx_demand_zones_timestamp ON demand_zones(timestamp);
