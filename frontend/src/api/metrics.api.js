import apiClient from './httpClient';

export const metricsApi = {
	// Get system metrics
	getSystemMetrics: async () => {
		const response = await apiClient.get('/metrics/system');
		return response.data;
	},

	// Get performance metrics
	getPerformance: async () => {
		const response = await apiClient.get('/metrics/performance');
		return response.data;
	}
};

export default metricsApi;
