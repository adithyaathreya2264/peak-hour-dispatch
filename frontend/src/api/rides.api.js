import apiClient from './httpClient';

export const ridesApi = {
	// Create ride request
	create: async (data) => {
		const response = await apiClient.post('/rides', data);
		return response.data;
	},

	// Get all rides
	getAll: async (status = null) => {
		const params = status ? { status_filter: status } : {};
		const response = await apiClient.get('/rides', { params });
		return response.data;
	},

	// Get ride by ID
	getById: async (rideId) => {
		const response = await apiClient.get(`/rides/${rideId}`);
		return response.data;
	},

	// Update ride
	update: async (rideId, data) => {
		const response = await apiClient.patch(`/rides/${rideId}`, data);
		return response.data;
	},

	// Create trip outcome
	createOutcome: async (data) => {
		const response = await apiClient.post('/rides/outcomes', data);
		return response.data;
	}
};

export default ridesApi;
