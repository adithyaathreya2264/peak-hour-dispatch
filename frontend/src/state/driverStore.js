import { create } from 'zustand';
import driversApi from '../api/drivers.api';

export const useDriverStore = create((set, get) => ({
	drivers: [],
	onlineDrivers: [],
	selectedDriver: null,
	loading: false,
	error: null,

	// Fetch all drivers
	fetchDrivers: async (onlineOnly = false) => {
		set({ loading: true, error: null });
		try {
			const data = await driversApi.getAll(onlineOnly);
			set({ drivers: data, loading: false });
		} catch (error) {
			set({ error: error.message, loading: false });
		}
	},

	// Fetch online driver locations
	fetchOnlineLocations: async () => {
		try {
			const data = await driversApi.getOnlineLocations();
			set({ onlineDrivers: data });
		} catch (error) {
			set({ error: error.message });
		}
	},

	// Select a driver
	selectDriver: (driver) => set({ selectedDriver: driver }),

	// Clear selection
	clearSelection: () => set({ selectedDriver: null }),
}));
