from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

if not OPENCAGE_API_KEY:
    logger.warning("OPENCAGE_API_KEY not found in environment variables")

# Application Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# Maps Configuration
MAPS_DIR = "maps"

# Tracker instance will be initialized in main.py
tracker = None