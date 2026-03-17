import { useState } from 'react';
import Navigation from './components/Navigation/Navigation';
import HeroSection from './components/HeroSection/HeroSection';
import MapView from './components/MapView/MapView';
import RideRequestPanel from './components/RideRequestPanel/RideRequestPanel';
import DriverCard from './components/DriverCard/DriverCard';
import MetricsDashboard from './components/MetricsDashboard/MetricsDashboard';
import StatsSection from './components/StatsSection/StatsSection';
import AboutSection from './components/AboutSection/AboutSection';
import { useRideStore } from './state/rideStore';
import './App.css';

function App() {
  const { matchedDrivers, currentRide } = useRideStore();
  const [showRideRequest, setShowRideRequest] = useState(false);
  const [activeView, setActiveView] = useState('dashboard'); // dashboard or metrics

  const handleRequestRide = () => {
    setShowRideRequest(true);
  };

  const handleCloseRideRequest = () => {
    setShowRideRequest(false);
  };

  const handleViewChange = (view) => {
    console.log('Changing view to:', view);
    setActiveView(view);
    // Close ride request modal if open when switching views
    if (showRideRequest) {
      setShowRideRequest(false);
    }
  };

  return (
    <div className="app">
      <Navigation onViewChange={handleViewChange} activeView={activeView} />

      {activeView === 'dashboard' ? (
        <>
          <main className="main-content">
            <div className="content-grid">
              <HeroSection
                onRequestRide={handleRequestRide}
                onViewMetrics={() => handleViewChange('metrics')}
              />

              <div className="map-container">
                <MapView />
              </div>
            </div>
          </main>

          {/* Ride Request Modal */}
          {showRideRequest && (
            <div className="modal-overlay" onClick={handleCloseRideRequest}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={handleCloseRideRequest}>
                  ×
                </button>
                <RideRequestPanel onClose={handleCloseRideRequest} />
              </div>
            </div>
          )}

          {/* Matched Drivers Sheet */}
          {currentRide && matchedDrivers.length > 0 && (
            <div className="drivers-sheet">
              <div className="sheet-container">
                <div className="sheet-header">
                  <h2>Top Matched Drivers</h2>
                  <p>Found {matchedDrivers.length} drivers ranked by acceptance-aware scoring</p>
                </div>
                <div className="drivers-grid">
                  {matchedDrivers.map((driver, index) => (
                    <DriverCard
                      key={driver.driver_id}
                      driver={driver}
                      rank={index + 1}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          <StatsSection />
        </>
      ) : activeView === 'metrics' ? (
        <div className="metrics-view">
          <div className="metrics-header">
            <button
              className="back-btn"
              onClick={() => handleViewChange('dashboard')}
            >
              ← Back to Dashboard
            </button>
          </div>
          <MetricsDashboard />
        </div>
      ) : activeView === 'about' ? (
        <AboutSection />
      ) : null}
    </div>
  );
}

export default App;
