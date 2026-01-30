import { create } from 'zustand';
import ridesApi from '../api/rides.api';
import matchingApi from '../api/matching.api';

export const useRideStore = create((set, get) => ({
	rides: [],
	currentRide: null,
	matchedDrivers: [],
	loading: false,
	error: null,

	// Create a new ride request
	createRide: async (rideData) => {
		set({ loading: true, error: null });
		try {
			const ride = await ridesApi.create(rideData);
			set({
				currentRide: ride,
				rides: [...get().rides, ride],
				loading: false
			});
			return ride;
		} catch (error) {
			set({ error: error.message, loading: false });
			throw error;
		}
	},

	// Find matching drivers for current ride
	findMatchingDrivers: async (rideId) => {
		set({ loading: true, error: null });
		try {
			const result = await matchingApi.findDrivers(rideId);
			set({
				matchedDrivers: result.matched_drivers,
				loading: false
			});
			return result;
		} catch (error) {
			set({ error: error.message, loading: false });
			throw error;
		}
	},

	// Fetch all rides
	fetchRides: async () => {
		set({ loading: true, error: null });
		try {
			const data = await ridesApi.getAll();
			set({ rides: data, loading: false });
		} catch (error) {
			set({ error: error.message, loading: false });
		}
	},

	// Clear current ride
	clearCurrentRide: () => set({
		currentRide: null,
		matchedDrivers: []
	}),
}));
