import apiClient from './httpClient';

export const matchingApi = {
	// Find matching drivers for a ride
	findDrivers: async (rideId, maxDrivers = 5) => {
		const response = await apiClient.post('/matching/find-drivers', {
			ride_id: rideId
		}, {
			params: { max_drivers: maxDrivers }
		});
		return response.data;
	}
};

export default matchingApi;
