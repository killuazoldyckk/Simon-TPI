# backend/crud.py

from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
import json


def load_users_from_json():
    """Membaca semua data pengguna dari file users.json."""
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Jika file tidak ada, kembalikan daftar kosong untuk menghindari error
        return []

def get_user_by_username(username: str):
    """Mencari pengguna berdasarkan username dari file JSON."""
    all_users = load_users_from_json()
    for user in all_users:
        if user.get('username') == username:
            return user
    return None

def get_users():
    """Mengambil semua pengguna dari file JSON."""
    return load_users_from_json()

def verify_password(plain_password, stored_password):
    """Memverifikasi password teks biasa (sederhana)."""
    return plain_password == stored_password

# --- FUNGSI UNTUK PENGGUNA ---

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(username: str):
    """Mencari pengguna berdasarkan username dari file JSON."""
    all_users = load_users_from_json()
    for user in all_users:
        if user['username'] == username: # <-- Ubah logika pencarian
            return user
    return None

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, photo_url: str):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        photo_url=photo_url,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- FUNGSI UNTUK MANIFEST, KRU, DLL. ---

def create_manifest(db: Session, manifest: schemas.ManifestCreate):
    # Buat objek Manifest tanpa penumpang dan kru terlebih dahulu
    db_manifest = models.Manifest(
        ship_name=manifest.ship_name,
        arrival_date=manifest.arrival_date,
        origin=manifest.origin,
        destination=manifest.destination,
        flag=manifest.flag,
        skipper_name=manifest.skipper_name,
        departure_date=manifest.departure_date,
    )

    db.add(db_manifest)
    db.flush() # Penting untuk mendapatkan ID manifest sebelum menambah penumpang/kru

    # Buat objek penumpang dan kru
    db_passengers = [models.Passenger(**p.dict(), manifest_id=db_manifest.id) for p in manifest.passengers]
    db_crews = [models.Crew(**c.dict(), manifest_id=db_manifest.id) for c in manifest.crews]
    
    db.add_all(db_passengers)
    db.add_all(db_crews)
    
    db.commit()
    db.refresh(db_manifest)
    return schemas.Manifest.from_orm(db_manifest)

def get_manifests(db: Session, skip: int = 0, limit: int = 100):
    db_manifests = db.query(models.Manifest).offset(skip).limit(limit).all()
    return [schemas.Manifest.from_orm(m) for m in db_manifests]


def get_manifest(db: Session, manifest_id: int):
    db_manifest = db.query(models.Manifest).filter(models.Manifest.id == manifest_id).first()
    if db_manifest:
        return schemas.Manifest.from_orm(db_manifest)
    return None

def update_crew_details(db: Session, crew_id: int, crew_data: schemas.CrewUpdate):
    db_crew = db.query(models.Crew).filter(models.Crew.id == crew_id).first()
    if not db_crew:
        return None
    
    update_data = crew_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_crew, key, value)
        
    db.commit()
    db.refresh(db_crew)
    return db_crew

def get_dashboard_stats(db: Session):
    total_manifests = db.query(models.Manifest).count()
    total_passengers = db.query(models.Passenger).count()
    male_passengers = db.query(models.Passenger).filter(models.Passenger.sex == "M").count()
    female_passengers = db.query(models.Passenger).filter(models.Passenger.sex == "F").count()

    if total_manifests > 0:
        avg_passengers = round(total_passengers / total_manifests, 1)
    else:
        avg_passengers = 0.0

    top_nat_query = (
        db.query(models.Passenger.nationality, func.count(models.Passenger.nationality).label("count"))
        .group_by(models.Passenger.nationality)
        .order_by(func.count(models.Passenger.nationality).desc())
        .first()
    )
    if top_nat_query:
        top_nationality = schemas.TopNationalityStat(
            nationality=top_nat_query.nationality, count=top_nat_query.count
        )
    else:
        top_nationality = schemas.TopNationalityStat(nationality="N/A", count=0)

    return schemas.DashboardStats(
        total_manifests=total_manifests,
        total_passengers=total_passengers,
        male_passengers=male_passengers,
        female_passengers=female_passengers,
        avg_passengers_per_manifest=avg_passengers,
        top_nationality=top_nationality,
    )

def get_enhanced_dashboard_stats(db: Session):
    # Implementasi detail untuk dasbor analitik bisa ditambahkan di sini jika diperlukan
    # Untuk saat ini, kita bisa mengembalikan data kosong atau data dummy
    return schemas.EnhancedDashboardStats(
        daily_traffic=[],
        route_comparison=[],
        nationality_distribution=[],
        age_gender_distribution=[]
    )

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def get_feedback(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()