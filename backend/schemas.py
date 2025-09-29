# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# --- SKEMA BARU UNTUK ANALITIK ---
class DailyTrafficStat(BaseModel):
    date: str
    passenger_count: int
    manifest_count: int

class RouteComparisonStat(BaseModel):
    route: str
    passenger_count: int

class NationalityDistributionStat(BaseModel):
    nationality: str
    count: int

class AgeGenderDistributionStat(BaseModel):
    age_group: str
    male_count: int
    female_count: int

class EnhancedDashboardStats(BaseModel):
    daily_traffic: List[DailyTrafficStat]
    route_comparison: List[RouteComparisonStat]
    nationality_distribution: List[NationalityDistributionStat]
    age_gender_distribution: List[AgeGenderDistributionStat]
# ----------------------------------

# --- TAMBAHKAN SKEMA CREW DI SINI ---
class CrewBase(BaseModel):
    name: str
    dob: Optional[date] = None
    # --- TAMBAHKAN DUA KOLOM BARU DI SINI ---
    passport_no: Optional[str] = None
    passport_expiry: Optional[date] = None
    # ----------------------------------------
    seaman_book_no: Optional[str] = None
    seaman_book_expiry: Optional[date] = None
    rank: Optional[str] = None

    class Config:
        from_attributes = True

class CrewCreate(CrewBase):
    pass

class Crew(CrewBase):
    id: int
# ------------------------------------

# --- TAMBAHKAN SKEMA BARU UNTUK UPDATE ---
class CrewUpdate(BaseModel):
    passport_no: Optional[str] = None
    passport_expiry: Optional[date] = None
# -----------------------------------------

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
    crews: List[CrewCreate] = [] # Pastikan baris ini ada

class Manifest(ManifestBase):
    id: int
    passengers: List[Passenger] = []
    crews: List[CrewCreate] = []

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

class FeedbackBase(BaseModel):
    rating: int
    comments: Optional[str] = None
    role: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    name: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

# --- TAMBAHKAN SKEMA BARU DI SINI ---
class UserInfo(BaseModel):
    name: str
    email: str
    role: str
    photo_url: str