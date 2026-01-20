from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes import drivers, rides, matching, incentives, metrics, demand

# Create FastAPI app
app = FastAPI(
    title="Peak Hour Dispatch AI",
    description="Intelligent dispatch & incentive system for ride-hailing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(drivers.router, prefix="/api/drivers", tags=["drivers"])
app.include_router(rides.router, prefix="/api/rides", tags=["rides"])
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
app.include_router(incentives.router, prefix="/api/incentives", tags=["incentives"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(demand.router, prefix="/api/demand", tags=["demand"])


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Peak Hour Dispatch AI starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API running on {settings.API_HOST}:{settings.API_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("⛔ Peak Hour Dispatch AI shutting down...")


@app.get("/")
async def root():
    return {
        "message": "Peak Hour Dispatch AI - Intelligent Ride Dispatch System",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
