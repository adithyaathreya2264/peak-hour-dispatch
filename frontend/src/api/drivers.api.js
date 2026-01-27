import apiClient from './httpClient';

export const driversApi = {
	// Get all drivers
	getAll: async (onlineOnly = false) => {
		const response = await apiClient.get('/drivers', {
			params: { online_only: onlineOnly }
		});
		return response.data;
	},

	// Get online driver locations
	getOnlineLocations: async () => {
		const response = await apiClient.get('/drivers/online/locations');
		return response.data;
	},

	// Get specific driver
	getById: async (driverId) => {
		const response = await apiClient.get(`/drivers/${driverId}`);
		return response.data;
	},

	// Update driver
	update: async (driverId, data) => {
		const response = await apiClient.patch(`/drivers/${driverId}`, data);
		return response.data;
	},

	// Create driver
	create: async (data) => {
		const response = await apiClient.post('/drivers', data);
		return response.data;
	}
};

export default driversApi;
