# backend/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

# --- SKEMA UNTUK LOGIN ---
class LoginRequest(BaseModel):
    username: str
    password: str


# 2. Skema-skema untuk Pengguna (User)
# Digunakan untuk membuat, menampilkan, dan memperbarui data pengguna.
class UserBase(BaseModel):
    name: str
    username: str
    role: str

class UserCreate(UserBase):
    password: str
    photo_url: Optional[str] = None

class User(UserBase):
    id: int
    photo_url: Optional[str] = None
    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    id: int
    name: str
    username: str # <-- UBAH DI SINI
    role: str
    photo_url: Optional[str] = None
    class Config:
        orm_mode = True

class UserInfo(UserBase): # Digunakan khusus untuk daftar pengguna
    id: int
    photo_url: Optional[str] = None
    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    name: str

# --- SKEMA UNTUK MANIFEST, PENUMPANG, DAN KRU ---
class CrewBase(BaseModel):
    name: str
    dob: Optional[date] = None
    passport_no: Optional[str] = None
    passport_expiry: Optional[date] = None
    seaman_book_no: Optional[str] = None
    seaman_book_expiry: Optional[date] = None
    rank: Optional[str] = None

class CrewCreate(CrewBase):
    pass

class Crew(CrewBase):
    id: int
    manifest_id: int
    class Config:
        orm_mode = True
        
class CrewUpdate(BaseModel):
    passport_no: Optional[str] = None
    passport_expiry: Optional[date] = None

class PassengerBase(BaseModel):
    name: str
    sex: Optional[str] = None
    birth_place: Optional[str] = None
    dob: Optional[date] = None
    nationality: Optional[str] = None
    passport_no: Optional[str] = None # Dibuat opsional agar lebih fleksibel
    remarks: Optional[str] = None

class PassengerCreate(PassengerBase):
    pass

class Passenger(PassengerBase):
    id: int
    manifest_id: int
    class Config:
        orm_mode = True

class ManifestBase(BaseModel):
    ship_name: str
    arrival_date: date
    origin: str
    destination: str
    flag: Optional[str] = None
    skipper_name: Optional[str] = None
    departure_date: Optional[date] = None

class ManifestCreate(ManifestBase):
    passengers: List[PassengerCreate] = []
    crews: List[CrewCreate] = []

class Manifest(ManifestBase):
    id: int
    passengers: List[Passenger] = []
    crews: List[Crew] = []
    class Config:
        orm_mode = True

# --- SKEMA UNTUK FEEDBACK & DASHBOARD ---
class FeedbackBase(BaseModel):
    rating: int
    comments: Optional[str] = None
    role: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    class Config:
        orm_mode = True # <-- PERBAIKAN DI SINI

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

