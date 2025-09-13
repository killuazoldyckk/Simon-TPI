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

class PassengerCreate(PassengerBase):
    pass

class Passenger(PassengerBase):
    id: int
    class Config:
        from_attributes = True

class ManifestBase(BaseModel):
    ship_name: str
    arrival_date: str
    origin: str
    destination: str

class ManifestCreate(ManifestBase):
    passengers: List[PassengerCreate] = []

class Manifest(ManifestBase):
    id: int
    passengers: List[Passenger] = []
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str
