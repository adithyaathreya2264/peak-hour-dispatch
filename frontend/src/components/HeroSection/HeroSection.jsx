import { useDriverStore } from '../../state/driverStore';
import { useRideStore } from '../../state/rideStore';
import './HeroSection.css';

const HeroSection = ({ onRequestRide, onViewMetrics }) => {
	const { onlineDrivers } = useDriverStore();
	const { rides } = useRideStore();

	const onlineCount = onlineDrivers.length;
	const totalRides = rides?.length || 0;

	return (
		<div className="hero-section">
			<div className="hero-content">
				<div className="hero-badge">
					<span className="badge-icon">✨</span>
					<span>AI-Powered Dispatch</span>
				</div>

				<h1 className="hero-title">
					Intelligent dispatch
					<br />
					system for peak hours
				</h1>

				<p className="hero-description">
					Leverage machine learning to predict ride denials, optimize driver
					matching, and reduce wait times by 30%. Smart incentives that boost
					acceptance rates during high-demand periods.
				</p>

				<div className="hero-actions">
					<button className="btn-primary" onClick={onRequestRide}>
						Request a Ride
					</button>
					<button className="btn-secondary" onClick={onViewMetrics}>
						<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
							<circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
							<path d="M10 10l5.66-5.66" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
						</svg>
						View Analytics
					</button>
				</div>

				<div className="hero-stats">
					<div className="stat-card">
						<div className="stat-icon">👥</div>
						<div className="stat-content">
							<div className="stat-value">{onlineCount}+</div>
							<div className="stat-label">Drivers Online</div>
						</div>
					</div>

					<div className="stat-card">
						<div className="stat-icon">🚗</div>
						<div className="stat-content">
							<div className="stat-value">{totalRides}+</div>
							<div className="stat-label">Active Rides</div>
						</div>
					</div>

					<div className="stat-card">
						<div className="stat-icon">⚡</div>
						<div className="stat-content">
							<div className="stat-value">87.5%</div>
							<div className="stat-label">Test Pass Rate</div>
						</div>
					</div>
				</div>

				<div className="hero-note">
					<span className="note-icon">★</span>
					<span>ML model achieves 68% accuracy in predicting ride denials</span>
				</div>
			</div>
		</div>
	);
};

export default HeroSection;
