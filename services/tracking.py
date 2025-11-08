import phonenumbers
from phonenumbers import geocoder, carrier
import folium
from opencage.geocoder import OpenCageGeocode
import os
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class PhoneTracker:
    
    def __init__(self, opencage_api_key: str = None):

        if not opencage_api_key:
            from dotenv import load_dotenv
            load_dotenv()
            opencage_api_key = os.getenv("OPENCAGE_API_KEY")
        
        if not opencage_api_key:
            raise ValueError("OPENCAGE_API_KEY is required. Set it in .env file or pass as argument")
        
        try:
            self.geocoder_instance = OpenCageGeocode(opencage_api_key)
            self.maps_dir = "maps"
            os.makedirs(self.maps_dir, exist_ok=True)
            logger.info("PhoneTracker initialized successfully")
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenCage Geocoder: {str(e)}")
    
    def parse_and_validate(self, phone_number: str) -> phonenumbers.PhoneNumber:
        parsed = phonenumbers.parse(phone_number.strip(), None)
        return parsed
    
    def get_location(self, parsed_number: phonenumbers.PhoneNumber) -> str:
        location = geocoder.description_for_number(parsed_number, "en")
        return location
    
    def get_service_provider(self, parsed_number: phonenumbers.PhoneNumber) -> str:
        provider = carrier.name_for_number(parsed_number, "en")
        return provider if provider else "Unknown"
    
    def geocode_location(self, location: str) -> Tuple[float, float]:
        results = self.geocoder_instance.geocode(location)

        lat = results[0]['geometry']['lat']
        lng = results[0]['geometry']['lng']
        
        return lat, lng
    
    def create_map(self, lat: float, lng: float, location: str, phone_number: str, map_id: str) -> str:
        map_file = os.path.join(self.maps_dir, f"map_{map_id}.html")
        
        map_obj = folium.Map(
            location=[lat, lng],
            zoom_start=9,
            tiles="OpenStreetMap"
        )
        
        folium.Marker(
            [lat, lng],
            popup=location,
            tooltip=f"Phone: {phone_number}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map_obj)
        
        map_obj.save(map_file)
        logger.info(f"Map saved: {map_file}")
        
        return map_file
    
    def track(self, phone_number: str) -> Dict:

        parsed_number = self.parse_and_validate(phone_number)
        
        location = self.get_location(parsed_number)
        service_provider = self.get_service_provider(parsed_number)
        
        lat, lng = self.geocode_location(location)
        
        map_id = f"{parsed_number.country_code}_{parsed_number.national_number}"
        map_file = self.create_map(lat, lng, location, phone_number, map_id)
        
        return {
            'phone_number': phone_number,
            'location': location,
            'service_provider': service_provider,
            'latitude': lat,
            'longitude': lng,
            'map_id': map_id,
            'map_file': map_file
        }