import './Navigation.css';

const Navigation = ({ onViewChange, activeView = 'dashboard' }) => {
  const handleNavClick = (view) => {
    if (onViewChange) {
      onViewChange(view);
    }
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-logo">
          <span className="logo-icon"></span>
          <span className="logo-text">Peak Hour Dispatch</span>
        </div>

        <div className="nav-links">
          <button
            className={`nav-link ${activeView === 'dashboard' ? 'active' : ''}`}
            onClick={() => handleNavClick('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`nav-link ${activeView === 'metrics' ? 'active' : ''}`}
            onClick={() => handleNavClick('metrics')}
          >
            Metrics
          </button>
          <button
            className={`nav-link ${activeView === 'about' ? 'active' : ''}`}
            onClick={() => handleNavClick('about')}
          >
            About
          </button>
        </div>

        <div className="nav-actions">
          <button
            className="action-btn"
            onClick={() => handleNavClick('metrics')}
          >
            View Analytics →
          </button>
        </div>

        <button className="mobile-menu-btn" aria-label="Menu">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
