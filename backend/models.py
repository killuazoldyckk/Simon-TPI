# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)
    manifests = relationship("Manifest", back_populates="uploader")

class Manifest(Base):
    __tablename__ = "manifests"
    id = Column(Integer, primary_key=True, index=True)
    ship_name = Column(String, index=True)
    voyage_date = Column(Date)
    file_url = Column(String)
    flag = Column(String, nullable=True)
    skipper_name = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploader = relationship("User", back_populates="manifests")
    passengers = relationship("Passenger", back_populates="manifest")

class Passenger(Base):
    __tablename__ = "passengers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    sex = Column(String)
    birth_place = Column(String)
    dob = Column(Date)
    nationality = Column(String)
    passport_no = Column(String)
    remarks = Column(String)
    manifest_id = Column(Integer, ForeignKey("manifests.id"))
    manifest = relationship("Manifest", back_populates="passengers")