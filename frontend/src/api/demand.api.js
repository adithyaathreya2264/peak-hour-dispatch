import apiClient from './httpClient';

export const demandApi = {
	// Get all zones
	getZones: async () => {
		const response = await apiClient.get('/demand/zones');
		return response.data;
	},

	// Get heatmap data
	getHeatmap: async () => {
		const response = await apiClient.get('/demand/heatmap');
		return response.data;
	},

	// Get top hotspots
	getHotspots: async (topN = 5) => {
		const response = await apiClient.get('/demand/hotspots', {
			params: { top_n: topN }
		});
		return response.data;
	}
};

export default demandApi;
