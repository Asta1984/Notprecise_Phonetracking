# Initialize PhoneTracker
try:
    OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
    if not OPENCAGE_API_KEY:
        raise ValueError("OPENCAGE_API_KEY not found in environment variables")
    tracker = PhoneTracker(OPENCAGE_API_KEY)
    logger.info("PhoneTracker initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PhoneTracker: {e}")
    tracker = None