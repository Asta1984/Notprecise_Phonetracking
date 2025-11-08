from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
import logging
from services.tracking import PhoneTracker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phone Tracker API")


@app.post("/track", response_model=TrackingResponse)
async def track_phone_number(request: PhoneNumberRequest):
    """
    Track phone number location, service provider, and generate map
    
    Args:
        request: PhoneNumberRequest with phone_number field
        
    Returns:
        TrackingResponse with location, coordinates, and map URL
        
    Raises:
        HTTPException: 400 for invalid input, 500 for server errors
    """
    try:
        if not tracker:
            raise HTTPException(
                status_code=500, 
                detail="Tracking service unavailable"
            )
        
        # Execute tracking
        result = tracker.track(request.phone_number)
        
        return TrackingResponse(
            phone_number=result['phone_number'],
            location=result['location'],
            service_provider=result['service_provider'],
            latitude=result['latitude'],
            longitude=result['longitude'],
            map_url=f"/map/{result['map_id']}"
        )
    
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Tracking error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/map/{map_id}")
async def get_map(map_id: str):
    """
    Retrieve generated map by ID
    
    Args:
        map_id: Map identifier in format 'country_code_number'
        
    Returns:
        HTML file response with Folium map
        
    Raises:
        HTTPException: 404 if map not found
    """
    try:
        map_file = f"maps/map_{map_id}.html"
        
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
            "GET /map/{map_id}": "Retrieve generated map",
            "GET /health": "Health check endpoint",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "Alternative API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)