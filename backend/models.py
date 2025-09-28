# backend/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from database import Base

class Manifest(Base):
    __tablename__ = "manifests"

    id = Column(Integer, primary_key=True, index=True)
    ship_name = Column(String, index=True)
    arrival_date = Column(String)
    origin = Column(String)
    destination = Column(String)
    
    # --- ADDED FIELDS ---
    flag = Column(String, nullable=True)
    skipper_name = Column(String, nullable=True)
    departure_date = Column(String, nullable=True)
    # --------------------

    passengers = relationship("Passenger", back_populates="manifest")
    # --- TAMBAHKAN RELASI BARU DI SINI ---
    crews = relationship("Crew", back_populates="manifest")

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

# --- TAMBAHKAN MODEL BARU DI SINI ---
class Crew(Base):
    __tablename__ = "crews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dob = Column(Date, nullable=True)
    seaman_book_no = Column(String)
    seaman_book_expiry = Column(Date, nullable=True)
    rank = Column(String) # Jabatan

    manifest_id = Column(Integer, ForeignKey("manifests.id"))
    manifest = relationship("Manifest", back_populates="crews")
    
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    role = Column(String, nullable=True)  # 'agen' or 'admin'