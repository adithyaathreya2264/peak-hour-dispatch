import './DriverCard.css';

const DriverCard = ({ driver, rank }) => {
	const {
		driver_id,
		distance,
		eta_minutes,
		acceptance_probability,
		overall_score,
		score_breakdown,
		prediction_source
	} = driver;

	// Color code based on acceptance probability
	const getAcceptanceColor = (prob) => {
		if (prob >= 0.7) return '#10b981'; // green
		if (prob >= 0.5) return '#f59e0b'; // amber
		return '#ef4444'; // red
	};

	const acceptanceColor = getAcceptanceColor(acceptance_probability);

	return (
		<div className="driver-card-modern">
			<div className="card-header">
				<div className="rank-badge">#{rank}</div>
				<div className="driver-info">
					<h3 className="driver-id">Driver {driver_id.slice(0, 8)}</h3>
					<div className="driver-meta">
						<span className="meta-item">
							<svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
								<path d="M7 0C3.69 0 1 2.69 1 6c0 3.75 6 8 6 8s6-4.25 6-8c0-3.31-2.69-6-6-6zm0 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" />
							</svg>
							{distance.toFixed(1)} km
						</span>
						<span className="meta-item">
							<svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
								<circle cx="7" cy="7" r="6" stroke="currentColor" strokeWidth="1" fill="none" />
								<path d="M7 3v4l3 2" />
							</svg>
							{eta_minutes} min
						</span>
					</div>
				</div>
				<div className="acceptance-badge" style={{ background: acceptanceColor }}>
					{(acceptance_probability * 100).toFixed(0)}%
				</div>
			</div>

			<div className="card-body">
				<div className="score-section">
					<div className="overall-score">
						<span className="score-label">Match Score</span>
						<span className="score-value">{(overall_score * 100).toFixed(0)}/100</span>
					</div>

					<div className="score-breakdown">
						<div className="breakdown-item">
							<span className="breakdown-label">Acceptance</span>
							<div className="breakdown-bar">
								<div
									className="breakdown-fill"
									style={{ width: `${score_breakdown.acceptance_component * 100}%`, background: '#10b981' }}
								/>
							</div>
							<span className="breakdown-value">{(score_breakdown.acceptance_component * 100).toFixed(0)}%</span>
						</div>

						<div className="breakdown-item">
							<span className="breakdown-label">ETA</span>
							<div className="breakdown-bar">
								<div
									className="breakdown-fill"
									style={{ width: `${score_breakdown.eta_component * 100}%`, background: '#3b82f6' }}
								/>
							</div>
							<span className="breakdown-value">{(score_breakdown.eta_component * 100).toFixed(0)}%</span>
						</div>

						<div className="breakdown-item">
							<span className="breakdown-label">Fairness</span>
							<div className="breakdown-bar">
								<div
									className="breakdown-fill"
									style={{ width: `${score_breakdown.fairness_component * 100}%`, background: '#8b5cf6' }}
								/>
							</div>
							<span className="breakdown-value">{(score_breakdown.fairness_component * 100).toFixed(0)}%</span>
						</div>
					</div>
				</div>

				<div className="card-footer">
					<span className="prediction-source">
						{prediction_source === 'ml' ? '🤖 ML Prediction' : '📊 Heuristic'}
					</span>
					<button className="assign-btn">Assign Driver</button>
				</div>
			</div>
		</div>
	);
};

export default DriverCard;
