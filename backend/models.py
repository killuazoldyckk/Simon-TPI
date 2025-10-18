# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(50)) # Misalnya: 'admin', 'agen'
    photo_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

class Manifest(Base):
    __tablename__ = "manifests"

    id = Column(Integer, primary_key=True, index=True)
    ship_name = Column(String(100), index=True)
    arrival_date = Column(Date)
    origin = Column(String(100))
    destination = Column(String(100))
    flag = Column(String(50), nullable=True)
    skipper_name = Column(String(100), nullable=True)
    departure_date = Column(Date, nullable=True)

    passengers = relationship("Passenger", back_populates="manifest", cascade="all, delete-orphan")
    crews = relationship("Crew", back_populates="manifest", cascade="all, delete-orphan")

class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    sex = Column(String(10), nullable=True)
    birth_place = Column(String(100), nullable=True)
    dob = Column(Date, nullable=True)
    nationality = Column(String(100), nullable=True)
    passport_no = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)

    manifest_id = Column(Integer, ForeignKey("manifests.id"))
    manifest = relationship("Manifest", back_populates="passengers")

class Crew(Base):
    __tablename__ = "crews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    dob = Column(Date, nullable=True)
    passport_no = Column(String(50), nullable=True)
    passport_expiry = Column(Date, nullable=True)
    seaman_book_no = Column(String(50), nullable=True)
    seaman_book_expiry = Column(Date, nullable=True)
    rank = Column(String(100), nullable=True) # Jabatan

    manifest_id = Column(Integer, ForeignKey("manifests.id"))
    manifest = relationship("Manifest", back_populates="crews")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    comments = Column(Text, nullable=True)
    role = Column(String(50))



