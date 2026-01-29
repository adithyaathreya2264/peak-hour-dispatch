import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useDriverStore } from '../../state/driverStore';
import { useRideStore } from '../../state/rideStore';
import demandApi from '../../api/demand.api';
import './MapView.css';

// IMPORTANT: Get a free token from https://www.mapbox.com/
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJja2V4YW1wbGUifQ.example';

const BANGALORE_CENTER = [77.5946, 12.9716];

const MapView = () => {
	const mapContainerRef = useRef(null);
	const mapRef = useRef(null);
	const markersRef = useRef([]);

	const { onlineDrivers, fetchOnlineLocations } = useDriverStore();
	const { currentRide } = useRideStore();

	const [mapLoaded, setMapLoaded] = useState(false);
	const [showHeatmap, setShowHeatmap] = useState(true);
	const [heatmapData, setHeatmapData] = useState([]);

	// Initialize map
	useEffect(() => {
		if (!mapContainerRef.current) return;

		mapRef.current = new mapboxgl.Map({
			container: mapContainerRef.current,
			style: 'mapbox://styles/mapbox/dark-v11',
			center: BANGALORE_CENTER,
			zoom: 12,
		});

		mapRef.current.on('load', () => {
			setMapLoaded(true);
		});

		// Add navigation controls
		mapRef.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

		return () => {
			if (mapRef.current) {
				mapRef.current.remove();
			}
		};
	}, []);

	// Fetch and update heatmap data
	useEffect(() => {
		if (!mapLoaded) return;

		const fetchHeatmapData = async () => {
			try {
				const data = await demandApi.getHeatmap();
				setHeatmapData(data);
			} catch (error) {
				console.error('Error fetching heatmap:', error);
			}
		};

		fetchHeatmapData();
		const interval = setInterval(fetchHeatmapData, 30000); // Update every 30s
		return () => clearInterval(interval);
	}, [mapLoaded]);

	// Update heatmap layer
	useEffect(() => {
		if (!mapLoaded || !mapRef.current) return;

		// Remove existing heatmap layers
		if (mapRef.current.getLayer('demand-heatmap')) {
			mapRef.current.removeLayer('demand-heatmap');
		}
		if (mapRef.current.getLayer('demand-heatmap-border')) {
			mapRef.current.removeLayer('demand-heatmap-border');
		}
		if (mapRef.current.getSource('demand-zones')) {
			mapRef.current.removeSource('demand-zones');
		}

		if (!showHeatmap || heatmapData.length === 0) return;

		// Create GeoJSON from heatmap data
		const geojson = {
			type: 'FeatureCollection',
			features: heatmapData.map(zone => {
				// Parse zone_id to get row and col
				const parts = zone.zone_id.split('_');
				const row = parseInt(parts[1]);
				const col = parseInt(parts[2]);

				// Calculate zone boundaries
				const LAT_MIN = 12.8;
				const LAT_MAX = 13.2;
				const LNG_MIN = 77.4;
				const LNG_MAX = 77.8;
				const LAT_STEP = (LAT_MAX - LAT_MIN) / 6;
				const LNG_STEP = (LNG_MAX - LNG_MIN) / 6;

				const south = LAT_MIN + (row * LAT_STEP);
				const north = south + LAT_STEP;
				const west = LNG_MIN + (col * LNG_STEP);
				const east = west + LNG_STEP;

				return {
					type: 'Feature',
					properties: {
						demand_score: zone.demand_score,
						requests: zone.request_count,
						drivers: zone.driver_count,
						zone_id: zone.zone_id
					},
					geometry: {
						type: 'Polygon',
						coordinates: [[
							[west, south],
							[east, south],
							[east, north],
							[west, north],
							[west, south]
						]]
					}
				};
			})
		};

		// Add source
		mapRef.current.addSource('demand-zones', {
			type: 'geojson',
			data: geojson
		});

		// Add fill layer
		mapRef.current.addLayer({
			id: 'demand-heatmap',
			type: 'fill',
			source: 'demand-zones',
			paint: {
				'fill-color': [
					'interpolate',
					['linear'],
					['get', 'demand_score'],
					0, 'rgba(0, 255, 0, 0.1)',
					0.3, 'rgba(255, 255, 0, 0.2)',
					0.6, 'rgba(255, 165, 0, 0.3)',
					1, 'rgba(255, 0, 0, 0.4)'
				],
				'fill-opacity': 0.6
			}
		});

		// Add border layer
		mapRef.current.addLayer({
			id: 'demand-heatmap-border',
			type: 'line',
			source: 'demand-zones',
			paint: {
				'line-color': '#ffffff',
				'line-width': 0.5,
				'line-opacity': 0.3
			}
		});

		// Add click popup
		mapRef.current.on('click', 'demand-heatmap', (e) => {
			const properties = e.features[0].properties;
			new mapboxgl.Popup()
				.setLngLat(e.lngLat)
				.setHTML(`
          <div style="padding: 8px; color: #333;">
            <strong>Zone ${properties.zone_id}</strong><br/>
            Demand Score: ${(properties.demand_score * 100).toFixed(0)}%<br/>
            Requests: ${properties.requests}<br/>
            Drivers: ${properties.drivers}
          </div>
        `)
				.addTo(mapRef.current);
		});

		// Cursor effects
		mapRef.current.on('mouseenter', 'demand-heatmap', () => {
			mapRef.current.getCanvas().style.cursor = 'pointer';
		});

		mapRef.current.on('mouseleave', 'demand-heatmap', () => {
			mapRef.current.getCanvas().style.cursor = '';
		});

	}, [mapLoaded, heatmapData, showHeatmap]);

	// Update driver markers
	useEffect(() => {
		if (!mapLoaded || !mapRef.current) return;

		// Clear existing markers
		markersRef.current.forEach(marker => marker.remove());
		markersRef.current = [];

		// Add driver markers
		onlineDrivers.forEach(driver => {
			const el = document.createElement('div');
			el.className = 'driver-marker';
			el.innerHTML = '🚗';
			el.style.fontSize = '24px';
			el.style.cursor = 'pointer';

			const marker = new mapboxgl.Marker(el)
				.setLngLat([driver.longitude, driver.latitude])
				.setPopup(
					new mapboxgl.Popup({ offset: 25 })
						.setHTML(`
              <div style="padding: 8px;">
                <strong>Driver ${driver.driver_id.slice(0, 8)}</strong><br/>
                <span style="color: #4ade80;">Online</span>
              </div>
            `)
				)
				.addTo(mapRef.current);

			markersRef.current.push(marker);
		});
	}, [mapLoaded, onlineDrivers]);

	// Add ride markers
	useEffect(() => {
		if (!mapLoaded || !mapRef.current || !currentRide) return;

		// Pickup marker
		const pickupEl = document.createElement('div');
		pickupEl.className = 'pickup-marker';
		pickupEl.innerHTML = '📍';
		pickupEl.style.fontSize = '30px';

		const pickupMarker = new mapboxgl.Marker(pickupEl)
			.setLngLat([currentRide.pickup_location_lng, currentRide.pickup_location_lat])
			.setPopup(
				new mapboxgl.Popup({ offset: 25 })
					.setHTML('<div style="padding: 8px;"><strong>Pickup Location</strong></div>')
			)
			.addTo(mapRef.current);

		// Dropoff marker
		const dropoffEl = document.createElement('div');
		dropoffEl.className = 'dropoff-marker';
		dropoffEl.innerHTML = '🏁';
		dropoffEl.style.fontSize = '30px';

		const dropoffMarker = new mapboxgl.Marker(dropoffEl)
			.setLngLat([currentRide.dropoff_location_lng, currentRide.dropoff_location_lat])
			.setPopup(
				new mapboxgl.Popup({ offset: 25 })
					.setHTML('<div style="padding: 8px;"><strong>Dropoff Location</strong></div>')
			)
			.addTo(mapRef.current);

		markersRef.current.push(pickupMarker, dropoffMarker);

		// Fit bounds to show both markers
		const bounds = new mapboxgl.LngLatBounds()
			.extend([currentRide.pickup_location_lng, currentRide.pickup_location_lat])
			.extend([currentRide.dropoff_location_lng, currentRide.dropoff_location_lat]);

		mapRef.current.fitBounds(bounds, { padding: 100 });

		return () => {
			pickupMarker.remove();
			dropoffMarker.remove();
		};
	}, [mapLoaded, currentRide]);

	// Fetch driver locations periodically
	useEffect(() => {
		fetchOnlineLocations();
		const interval = setInterval(fetchOnlineLocations, 10000); // Every 10s
		return () => clearInterval(interval);
	}, [fetchOnlineLocations]);

	return (
		<div className="map-view">
			<div ref={mapContainerRef} className="map-container" />
			<div className="map-controls">
				<button
					className={`toggle-heatmap ${showHeatmap ? 'active' : ''}`}
					onClick={() => setShowHeatmap(!showHeatmap)}
				>
					{showHeatmap ? '🔥 Hide Heatmap' : '🗺️ Show Heatmap'}
				</button>
			</div>
		</div>
	);
};

export default MapView;
