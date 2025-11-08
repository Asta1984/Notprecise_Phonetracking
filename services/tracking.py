import phonenumbers
from phonenumbers import geocoder, carrier
import folium
from opencage.geocoder import OpenCageGeocode
import os
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class PhoneTracker:
    """Core phone tracking functionality"""
    
    def __init__(self, opencage_api_key: str):
        """
        Initialize tracker with OpenCage API key
        
        Args:
            opencage_api_key: OpenCage Geocoding API key
            
        Raises:
            ValueError: If API key is not provided
        """
        if not opencage_api_key:
            raise ValueError("OPENCAGE_API_KEY is required")
        
        self.geocoder_instance = OpenCageGeocode(opencage_api_key)
        self.maps_dir = "maps"
        os.makedirs(self.maps_dir, exist_ok=True)
    
    def parse_and_validate(self, phone_number: str) -> phonenumbers.PhoneNumber:
        """
        Parse and validate phone number
        
        Args:
            phone_number: Phone number string with country code
            
        Returns:
            Parsed phone number object
            
        Raises:
            ValueError: If phone number is invalid
        """
        try:
            parsed = phonenumbers.parse(phone_number.strip(), None)
        except phonenumbers.NumberParseException as e:
            raise ValueError(f"Invalid phone number format: {str(e)}")
        
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number")
        
        return parsed
    
    def get_location(self, parsed_number: phonenumbers.PhoneNumber) -> str:
        """
        Get location from phone number
        
        Args:
            parsed_number: Parsed phone number object
            
        Returns:
            Location string
            
        Raises:
            ValueError: If location cannot be determined
        """
        location = geocoder.description_for_number(parsed_number, "en")
        
        if not location:
            raise ValueError("Could not determine location for this phone number")
        
        return location
    
    def get_service_provider(self, parsed_number: phonenumbers.PhoneNumber) -> str:
        """
        Get service provider from phone number
        
        Args:
            parsed_number: Parsed phone number object
            
        Returns:
            Service provider name or "Unknown"
        """
        provider = carrier.name_for_number(parsed_number, "en")
        return provider if provider else "Unknown"
    
    def geocode_location(self, location: str) -> Tuple[float, float]:
        """
        Convert location to coordinates
        
        Args:
            location: Location string
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            ValueError: If geocoding fails
        """
        try:
            results = self.geocoder_instance.geocode(location)
        except Exception as e:
            raise ValueError(f"Geocoding failed: {str(e)}")
        
        if not results:
            raise ValueError(f"Could not find coordinates for location: {location}")
        
        lat = results[0]['geometry']['lat']
        lng = results[0]['geometry']['lng']
        
        return lat, lng
    
    def create_map(self, lat: float, lng: float, location: str, 
                   phone_number: str, map_id: str) -> str:
        """
        Create and save Folium map
        
        Args:
            lat: Latitude
            lng: Longitude
            location: Location name
            phone_number: Phone number string
            map_id: Unique map identifier
            
        Returns:
            Path to saved map file
        """
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
        """
        Complete tracking workflow
        
        Args:
            phone_number: Phone number string with country code
            
        Returns:
            Dictionary with tracking results:
            {
                'phone_number': str,
                'location': str,
                'service_provider': str,
                'latitude': float,
                'longitude': float,
                'map_id': str,
                'map_file': str
            }
            
        Raises:
            ValueError: If any step in tracking fails
        """
        # Parse and validate
        parsed_number = self.parse_and_validate(phone_number)
        
        # Get location and service provider
        location = self.get_location(parsed_number)
        service_provider = self.get_service_provider(parsed_number)
        
        # Geocode to get coordinates
        lat, lng = self.geocode_location(location)
        
        # Create map
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