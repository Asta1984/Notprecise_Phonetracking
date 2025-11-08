from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import logging
from models.schemas import TrackingResponse, PhoneNumberRequest
from services.tracking import PhoneTracker
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phone Tracker API")

# Initialize tracker at startup
tracker = None

@app.on_event("startup")
async def startup_event():
    """Initialize tracker on application startup"""
    global tracker
    try:
        if not config.OPENCAGE_API_KEY:
            raise ValueError("OPENCAGE_API_KEY not found in environment variables")
        
        tracker = PhoneTracker(config.OPENCAGE_API_KEY)
        logger.info("PhoneTracker initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize PhoneTracker: {e}")
        tracker = None

@app.post("/track", response_model=TrackingResponse)
async def track_phone_number(request: PhoneNumberRequest):
    result = tracker.track(request.phone_number)
    return TrackingResponse(
        phone_number=result['phone_number'],
        location=result['location'],
        service_provider=result['service_provider'],
        latitude=result['latitude'],
        longitude=result['longitude'],
        map_url=f"/map/{result['map_id']}"
    )
    
@app.get("/map/{map_id}")
async def get_map(map_id: str):
    try:
        map_file = os.path.join(config.MAPS_DIR, f"map_{map_id}.html")
        
        if not os.path.exists(map_file):
            raise HTTPException(status_code=404, detail="Map not found")
        
        return FileResponse(map_file, media_type="text/html")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Map retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving map")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Status and service information
    """
    return {
        "status": "healthy",
        "service": "Phone Tracker API",
        "tracking_service": "available" if tracker else "unavailable"
    }

@app.get("/")
async def root():
    """
    API documentation and endpoint information
    
    Returns:
        API metadata and available endpoints
    """
    return {
        "title": "Phone Tracker API",
        "version": "1.0.0",
        "description": "Track phone numbers and visualize their locations on maps",
        "endpoints": {
            "POST /track": "Track phone number and get location data",
            "GET /health": "Health check endpoint",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD
    )