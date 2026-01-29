import { useState } from 'react';
import { useRideStore } from '../../state/rideStore';
import './RideRequestPanel.css';

// Bangalore coordinates (rough bounds)
const BANGALORE_LAT_MIN = 12.8;
const BANGALORE_LAT_MAX = 13.2;
const BANGALORE_LNG_MIN = 77.4;
const BANGALORE_LNG_MAX = 77.8;

const randomLocation = () => {
	const lat = Math.random() * (BANGALORE_LAT_MAX - BANGALORE_LAT_MIN) + BANGALORE_LAT_MIN;
	const lng = Math.random() * (BANGALORE_LNG_MAX - BANGALORE_LNG_MIN) + BANGALORE_LNG_MIN;
	return { lat: parseFloat(lat.toFixed(6)), lng: parseFloat(lng.toFixed(6)) };
};

const RideRequestPanel = ({ onClose }) => {
	const { createRide, findMatchingDrivers, loading } = useRideStore();

	const [formData, setFormData] = useState({
		rider_name: 'Test Rider',
		pickup_location_lat: 12.9716,
		pickup_location_lng: 77.5946,
		dropoff_location_lat: 12.9916,
		dropoff_location_lng: 77.6146,
		traffic_score: 0.5,
		demand_multiplier: 1.0,
	});

	const handleChange = (e) => {
		const { name, value } = e.target;
		setFormData(prev => ({
			...prev,
			[name]: parseFloat(value) || value
		}));
	};

	const handleRandomize = () => {
		const pickup = randomLocation();
		const dropoff = randomLocation();
		setFormData(prev => ({
			...prev,
			pickup_location_lat: pickup.lat,
			pickup_location_lng: pickup.lng,
			dropoff_location_lat: dropoff.lat,
			dropoff_location_lng: dropoff.lng,
		}));
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		try {
			const ride = await createRide(formData);
			console.log('Ride created:', ride);

			// Find matching drivers
			await findMatchingDrivers(ride.ride_id);

			// Close modal after successful creation
			if (onClose) {
				onClose();
			}
		} catch (error) {
			console.error('Error creating ride:', error);
		}
	};

	return (
		<div className="ride-request-panel">
			<h2>🚕 Request a Ride</h2>
			<form onSubmit={handleSubmit}>
				<div className="form-group">
					<label>Rider Name</label>
					<input
						type="text"
						name="rider_name"
						value={formData.rider_name}
						onChange={handleChange}
					/>
				</div>

				<div className="location-section">
					<h3>📍 Pickup Location</h3>
					<div className="location-inputs">
						<input
							type="number"
							name="pickup_location_lat"
							placeholder="Latitude"
							value={formData.pickup_location_lat}
							onChange={handleChange}
							step="0.000001"
						/>
						<input
							type="number"
							name="pickup_location_lng"
							placeholder="Longitude"
							value={formData.pickup_location_lng}
							onChange={handleChange}
							step="0.000001"
						/>
					</div>
				</div>

				<div className="location-section">
					<h3>🏁 Dropoff Location</h3>
					<div className="location-inputs">
						<input
							type="number"
							name="dropoff_location_lat"
							placeholder="Latitude"
							value={formData.dropoff_location_lat}
							onChange={handleChange}
							step="0.000001"
						/>
						<input
							type="number"
							name="dropoff_location_lng"
							placeholder="Longitude"
							value={formData.dropoff_location_lng}
							onChange={handleChange}
							step="0.000001"
						/>
					</div>
				</div>

				<button type="button" onClick={handleRandomize} className="random-btn">
					🎲 Random Locations
				</button>

				<div className="form-group">
					<label>Traffic Score: {formData.traffic_score}</label>
					<input
						type="range"
						name="traffic_score"
						min="0"
						max="1"
						step="0.1"
						value={formData.traffic_score}
						onChange={handleChange}
					/>
					<small>0 = No traffic, 1 = Heavy traffic</small>
				</div>

				<div className="form-group">
					<label>Demand Multiplier: {formData.demand_multiplier}x</label>
					<input
						type="range"
						name="demand_multiplier"
						min="1"
						max="3"
						step="0.1"
						value={formData.demand_multiplier}
						onChange={handleChange}
					/>
					<small>Surge pricing multiplier</small>
				</div>

				<button type="submit" className="submit-btn" disabled={loading}>
					{loading ? 'Creating...' : '🚀 Request Ride & Find Drivers'}
				</button>
			</form>
		</div>
	);
};

export default RideRequestPanel;
