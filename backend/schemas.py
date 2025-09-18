# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PassengerBase(BaseModel):
    name: str
    sex: Optional[str] = None
    birth_place: Optional[str] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    passport_no: str
    remarks: Optional[str] = None

    class Config:
        from_attributes = True

class PassengerCreate(PassengerBase):
    pass

class Passenger(PassengerBase):
    id: int

class ManifestBase(BaseModel):
    ship_name: str
    arrival_date: str
    origin: str
    destination: str
    
    # --- ADDED FIELDS ---
    flag: Optional[str] = None
    skipper_name: Optional[str] = None
    departure_date: Optional[str] = None
    # --------------------

    class Config:
        from_attributes = True

class ManifestCreate(ManifestBase):
    passengers: List[PassengerCreate] = []

class Manifest(ManifestBase):
    id: int
    passengers: List[Passenger] = []

class LoginRequest(BaseModel):
    email: str
    password: str

class TopNationalityStat(BaseModel):
    nationality: Optional[str] = "N/A"
    count: int = 0

class DashboardStats(BaseModel):
    total_manifests: int
    total_passengers: int
    male_passengers: int
    female_passengers: int
    avg_passengers_per_manifest: float
    top_nationality: TopNationalityStat

class TokenResponse(BaseModel):
    """Skema response untuk login, menyertakan token JWT dan role."""
    access_token: str
    token_type: str
    role: str