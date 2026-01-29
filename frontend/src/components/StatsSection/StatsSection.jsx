import './StatsSection.css';

const StatsSection = () => {
	return (
		<section className="stats-section">
			<div className="stats-container">
				<div className="stats-grid">
					<div className="stat-item">
						<div className="stat-avatars">
							<div className="avatar">👤</div>
							<div className="avatar">👤</div>
							<div className="avatar">👤</div>
							<div className="avatar">+</div>
						</div>
						<div className="stat-info">
							<div className="stat-number">20+</div>
							<div className="stat-text">Active Drivers</div>
						</div>
					</div>

					<div className="stat-item">
						<div className="stat-info">
							<div className="stat-number">100+</div>
							<div className="stat-text">Total Trips</div>
						</div>
					</div>

					<div className="stat-item">
						<div className="stat-info">
							<div className="stat-number">87.5%</div>
							<div className="stat-text">API Test Pass Rate</div>
						</div>
					</div>

					<div className="stat-item powered-by">
						<div className="powered-heading">Powered by:</div>
						<div className="tech-logos">
							<span className="tech-logo">🗺️ Mapbox</span>
							<span className="tech-logo">🤖 XGBoost</span>
							<span className="tech-logo">⚡ FastAPI</span>
						</div>
					</div>
				</div>
			</div>
		</section>
	);
};

export default StatsSection;
