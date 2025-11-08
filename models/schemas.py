from pydantic import BaseModel

class PhoneNumberRequest(BaseModel):
    phone_number: str

class TrackingResponse(BaseModel):
    phone_number: str
    location: str
    service_provider: str
    latitude: float
    longitude: float
    map_url: str
