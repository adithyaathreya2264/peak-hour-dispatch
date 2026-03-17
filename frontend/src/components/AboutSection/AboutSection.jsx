import './AboutSection.css';

const AboutSection = () => {
	return (
		<div className="about-section">
			<div className="about-container">
				<div className="about-header">
					<h1>About Peak Hour Dispatch</h1>
					<p className="about-subtitle">AI-Powered Intelligent Dispatch System</p>
				</div>

				<div className="about-content">
					<div className="about-card">
						<div className="card-icon"></div>
						<h3>Machine Learning Powered</h3>
						<p>
							Uses XGBoost machine learning model to predict driver acceptance
							probability with 68% accuracy, enabling smarter dispatch decisions
							during peak hours.
						</p>
					</div>

					<div className="about-card">
						<div className="card-icon"></div>
						<h3>Intelligent Matching</h3>
						<p>
							Advanced scoring algorithm considers acceptance probability (45%),
							ETA (35%), and fairness (20%) to match riders with the most
							suitable drivers.
						</p>
					</div>

					<div className="about-card">
						<div className="card-icon"></div>
						<h3>Dynamic Incentives</h3>
						<p>
							Smart incentive system that offers cash bonuses to drivers when
							acceptance probability is low, boosting acceptance rates during
							high-demand periods.
						</p>
					</div>

					<div className="about-card">
						<div className="card-icon"></div>
						<h3>Real-time Heatmaps</h3>
						<p>
							Visual demand forecasting with geographic heatmaps showing
							high-demand zones, helping optimize driver positioning and
							reduce wait times by 30%.
						</p>
					</div>
				</div>

				<div className="about-tech">
					<h2>Technology Stack</h2>
					<div className="tech-grid">
						<div className="tech-item">
							<strong>Backend:</strong> FastAPI, Python, PostgreSQL (Supabase)
						</div>
						<div className="tech-item">
							<strong>Frontend:</strong> React, Vite, Mapbox GL JS
						</div>
						<div className="tech-item">
							<strong>ML/AI:</strong> XGBoost, Prophet (forecasting)
						</div>
						<div className="tech-item">
							<strong>Infrastructure:</strong> Redis, Kafka, Docker
						</div>
					</div>
				</div>

				<div className="about-footer">
					<p>Built as a demonstration of intelligent dispatch systems for ride-hailing platforms</p>
				</div>
			</div>
		</div>
	);
};

export default AboutSection;
