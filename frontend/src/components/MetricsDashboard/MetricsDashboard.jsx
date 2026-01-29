import { useEffect, useState } from 'react';
import metricsApi from '../../api/metrics.api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './MetricsDashboard.css';

const COLORS = ['#4ade80', '#f87171', '#fbbf24', '#60a5fa'];

const MetricsDashboard = () => {
	const [systemMetrics, setSystemMetrics] = useState(null);
	const [performanceMetrics, setPerformanceMetrics] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchMetrics();
		const interval = setInterval(fetchMetrics, 15000); // Refresh every 15s
		return () => clearInterval(interval);
	}, []);

	const fetchMetrics = async () => {
		try {
			const [system, performance] = await Promise.all([
				metricsApi.getSystemMetrics(),
				metricsApi.getPerformance()
			]);
			setSystemMetrics(system);
			setPerformanceMetrics(performance);
			setLoading(false);
		} catch (error) {
			console.error('Error fetching metrics:', error);
			setLoading(false);
		}
	};

	if (loading || !systemMetrics) {
		return <div className="metrics-loading">Loading metrics...</div>;
	}

	const rideData = [
		{ name: 'Completed', value: systemMetrics.completed_rides, color: '#4ade80' },
		{ name: 'Pending', value: systemMetrics.pending_rides, color: '#fbbf24' },
	];

	const driverData = [
		{ name: 'Online', value: systemMetrics.online_drivers, color: '#4ade80' },
		{ name: 'Offline', value: systemMetrics.total_drivers - systemMetrics.online_drivers, color: '#6b7280' },
	];

	return (
		<div className="metrics-dashboard">
			<h2>📊 System Metrics</h2>

			<div className="metrics-grid">
				<div className="metric-card">
					<div className="metric-icon">🚗</div>
					<div className="metric-content">
						<div className="metric-label">Total Rides</div>
						<div className="metric-value">{systemMetrics.total_rides}</div>
					</div>
				</div>

				<div className="metric-card">
					<div className="metric-icon">👥</div>
					<div className="metric-content">
						<div className="metric-label">Online Drivers</div>
						<div className="metric-value">
							{systemMetrics.online_drivers} / {systemMetrics.total_drivers}
						</div>
					</div>
				</div>

				<div className="metric-card">
					<div className="metric-icon">✅</div>
					<div className="metric-content">
						<div className="metric-label">Acceptance Rate</div>
						<div className="metric-value">{systemMetrics.avg_acceptance_rate.toFixed(1)}%</div>
					</div>
				</div>

				<div className="metric-card">
					<div className="metric-icon">⏱️</div>
					<div className="metric-content">
						<div className="metric-label">Avg Wait Time</div>
						<div className="metric-value">{systemMetrics.avg_wait_time_minutes} min</div>
					</div>
				</div>

				<div className="metric-card">
					<div className="metric-icon">💰</div>
					<div className="metric-content">
						<div className="metric-label">Incentives Offered</div>
						<div className="metric-value">{systemMetrics.total_incentives_offered}</div>
					</div>
				</div>

				<div className="metric-card">
					<div className="metric-icon">💵</div>
					<div className="metric-content">
						<div className="metric-label">Incentive Cost</div>
						<div className="metric-value">₹{systemMetrics.total_incentive_cost}</div>
					</div>
				</div>
			</div>

			{performanceMetrics && (
				<div className="performance-section">
					<h3>Performance Analytics</h3>
					<div className="performance-stats">
						<div className="perf-stat">
							<span>Overall Acceptance Rate:</span>
							<strong>{performanceMetrics.overall_acceptance_rate.toFixed(1)}%</strong>
						</div>
						<div className="perf-stat">
							<span>Incentive Effectiveness:</span>
							<strong>{performanceMetrics.incentive_effectiveness_rate.toFixed(1)}%</strong>
						</div>
						<div className="perf-stat">
							<span>Total Outcomes:</span>
							<strong>{performanceMetrics.total_trip_outcomes}</strong>
						</div>
					</div>

					<div className="charts-grid">
						<div className="chart-container">
							<h4>Ride Status Distribution</h4>
							<ResponsiveContainer width="100%" height={200}>
								<PieChart>
									<Pie
										data={rideData}
										dataKey="value"
										nameKey="name"
										cx="50%"
										cy="50%"
										outerRadius={70}
										label
									>
										{rideData.map((entry, index) => (
											<Cell key={`cell-${index}`} fill={entry.color} />
										))}
									</Pie>
									<Tooltip />
									<Legend />
								</PieChart>
							</ResponsiveContainer>
						</div>

						<div className="chart-container">
							<h4>Driver Availability</h4>
							<ResponsiveContainer width="100%" height={200}>
								<PieChart>
									<Pie
										data={driverData}
										dataKey="value"
										nameKey="name"
										cx="50%"
										cy="50%"
										outerRadius={70}
										label
									>
										{driverData.map((entry, index) => (
											<Cell key={`cell-${index}`} fill={entry.color} />
										))}
									</Pie>
									<Tooltip />
									<Legend />
								</PieChart>
							</ResponsiveContainer>
						</div>
					</div>
				</div>
			)}
		</div>
	);
};

export default MetricsDashboard;
