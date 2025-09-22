# backend/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_manifest(db: Session, manifest: schemas.ManifestCreate, file_url: str, user_id: int):
    db_passengers = [models.Passenger(**p.model_dump()) for p in manifest.passengers]
    db_manifest = models.Manifest(
        ship_name=manifest.ship_name,
        voyage_date=manifest.voyage_date,
        file_url=file_url,
        uploaded_by=user_id,
        flag=manifest.flag,
        skipper_name=manifest.skipper_name,
        origin=manifest.origin,
        destination=manifest.destination,
        arrival_date=manifest.arrival_date,
        departure_date=manifest.departure_date,
        passengers=db_passengers
    )
    db.add(db_manifest)
    db.commit()
    db.refresh(db_manifest)
    return db_manifest

def get_manifests(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Manifest)
        .options(joinedload(models.Manifest.uploader), joinedload(models.Manifest.passengers))
        .offset(skip).limit(limit).all()
    )

def get_manifest(db: Session, manifest_id: int):
    return (
        db.query(models.Manifest)
        .options(joinedload(models.Manifest.uploader), joinedload(models.Manifest.passengers))
        .filter(models.Manifest.id == manifest_id).first()
    )

def get_dashboard_stats(db: Session):
    total_manifests = db.query(models.Manifest).count()
    total_passengers = db.query(models.Passenger).count()
    male_passengers = db.query(models.Passenger).filter(models.Passenger.sex == "M").count()
    female_passengers = db.query(models.Passenger).filter(models.Passenger.sex == "F").count()
    avg_passengers = (total_passengers / total_manifests) if total_manifests > 0 else 0.0
    top_nat_query = (db.query(models.Passenger.nationality, func.count(models.Passenger.nationality).label("count"))
                     .group_by(models.Passenger.nationality).order_by(func.count(models.Passenger.nationality).desc()).first())
    top_nationality = schemas.TopNationalityStat(nationality=top_nat_query.nationality, count=top_nat_query.count) if top_nat_query else schemas.TopNationalityStat()
    return schemas.DashboardStats(
        total_manifests=total_manifests, total_passengers=total_passengers,
        male_passengers=male_passengers, female_passengers=female_passengers,
        avg_passengers_per_manifest=round(avg_passengers, 1),
        top_nationality=top_nationality
    )