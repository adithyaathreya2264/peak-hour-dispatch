# Peak Hour Dispatch AI

An intelligent, AI-powered dispatch & incentive system designed to predict ride denials during peak hours. By leveraging proactive driver nudges and smart matching algorithms, this system significantly reduces rider wait times and driver churn.

## What This Is

Peak Hour Dispatch AI is a **decision intelligence layer** that acts as the brain behind a ride-hailing operation. It's not just a map with icons; it's a high-fidelity matching engine that predicts human behavior and optimizes marketplace efficiency in real-time.

---

## Features (v2.0 - Refined UI)

### Modern Desktop-First UI
A premium, dark-themed (with glassmorphism elements) and desktop-optimized interface featuring:
- **Hero Dashboard**: A 40/60 split-panel layout for immediate context and live map visualization.
- **Interactive Mapbox Integration**: Real-time driver locations, ride markers, and dynamic demand heatmaps.
- **Full Metrics Suite**: Comprehensive analytics dashboard tracking system efficiency, driver fairness, and incentive ROI.
- **Clean Navigation**: Seamlessly switch between the **Live Dispatch Dashboard**, **Deep Analytics**, and **About** views.

### Ride Denial Prediction (XGBoost)
A machine learning model predicts the probability of a driver accepting a specific ride request. It analyzes:
- Trip distance, traffic conditions, and surge multipliers.
- Driver-specific features like current fatigue scores and historical acceptance rates.
- **Accuracy**: achieving ~68% accuracy in real-world simulations.

### Dynamic Incentive Engine
Proactively nudges drivers with smart incentives (e.g., ₹20 cash bonuses or streak rewards) when our ML model predicts a high probability of denial (P(accept) < 0.4).

### Acceptance-Aware Matching
Our matching engine deviates from "nearest-first" to "best-fit" by scoring drivers on a weighted profile:
- **45%** Acceptance probability (ML predicted)
- **35%** ETA / Distance score
- **20%** Fairness and load-balancing score

### Demand Forecasting & Heatmaps
Utilizes **FBProphet** to forecast zone-level demand trends, visualized through interactive Mapbox heatmaps. Drivers are nudged toward high-demand "hotspots" before peak hours begin.

---

## Architecture

```
        ┌──────────────────────────────────┐
        │        Browser (Web App)         │
        │      (React + Mapbox + CSS3)     │
        └────────────────┬─────────────────┘
                         │
        ┌────────────────▼─────────────────┐
        │       Backend API (FastAPI)      │
        │   (REST, WebSockets, Logic)      │
        └────────────────┬─────────────────┘
                         │
        ┌────────────────┴─────────────────┐
        │     Core Intelligence Layer      │
        ├──────────────────────────────────┤
        │ • Matching Engine (Scoring)      │
        │ • Denial Prediction (XGBoost)    │
        │ • Incentive Engine (Rules)       │
        └────────────────┬─────────────────┘
                         │
        ┌────────────────┴─────────────────┐
        │        Data & Event Layer        │
        ├──────────────────────────────────┤
        │ • PostgreSQL (Transactional)     │
        │ • Redis (Caching/Signals)        │
        │ • Kafka (Event Streaming)        │
        └──────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **React.js (Vite)** - Blazing fast UI development.
- **Mapbox GL JS** - High-performance geospatial visualization.
- **Zustand** - Lightweight state management.
- **Recharts** - Minimalist data visualization.
- **Vanilla CSS3** - Custom design system with modern aesthetics.

### Backend
- **FastAPI** - Modern, high-performance Python framework.
- **SQLAlchemy** - Powerful ORM for database operations.
- **Supabase / PostgreSQL** - Enterprise-grade relational storage.
- **Redis & Kafka** - Real-time signaling and event-driven architecture.

### Machine Learning
- **XGBoost** - Gradient boosting for high-accuracy predictions.
- **FBProphet** - Additive modeling for demand forecasting.
- **scikit-learn** - Evaluation metrics and feature engineering.

---

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account (or local PostgreSQL)
- Mapbox API Token

### Installation

1. **Clone & Install Backend**
```bash
git clone https://github.com/yourusername/peak-hour-dispatch-ai.git
cd peak-hour-dispatch-ai
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/app/requirements.txt
```

2. **Initialize Database**
Ensure your `.env` file contains a valid `DATABASE_URL`.
```bash
python data/synthetic/generate_data.py # Populates DB with mock data
```

3. **Install Frontend**
```bash
cd frontend
npm install
```

4. **Run the System**
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 6050 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## Project Structure

```bash
peak-hour-dispatch-ai/
├── backend/app/           # FastAPI app (routes, models, schemas)
├── frontend/src/          # React components & design system
├── ml-notebooks/          # Model training & exploration
├── data/synthetic/        # Mock data generation
├── infra/postgres/        # DB schema & migrations
└── documentation/         # System architecture & logic docs
```

---

## System Impacts
- **Wait Time Reduction**: Targeted 30% improvement in rider ETAs.
- **Acceptance Uplift**: ~25% higher driver acceptance during peak surges.
- **Marketplace Stability**: Reduced driver churn through fair matching and streak rewards.

---