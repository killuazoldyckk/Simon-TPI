# backend/crud.py

from sqlalchemy import func, case
from datetime import date, datetime, timedelta
import pandas as pd

from passlib.context import CryptContext
from sqlalchemy.orm import Session, selectinload

import models
import schemas
import json

from typing import List, Optional

OUR_PORT_NAME = "Pelabuhan TPI Teluk Nibung"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi password teks biasa dengan password yang sudah di-hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Menghasilkan hash dari password."""
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    """Mencari pengguna berdasarkan username dari database."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session):
    """Mengambil semua pengguna dari database."""
    return db.query(models.User).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Membuat pengguna baru di database dengan password yang di-hash."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        photo_url=user.photo_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

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

def delete_manifest(db: Session, manifest_id: int):
    """Menghapus manifest berdasarkan ID."""
    manifest = db.query(models.Manifest).filter(models.Manifest.id == manifest_id).first()
    if not manifest:
        return None
    db.delete(manifest)
    db.commit()
    return manifest

def get_enhanced_dashboard_stats(db: Session) -> schemas.EnhancedDashboardStats:
    """
    Mengambil dan mengagregasi semua data yang diperlukan untuk dasbor analitik.
    """
    
    # --- 1. Daily Traffic (30 hari terakhir) ---
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    manifests_query = db.query(
        models.Manifest.arrival_date,
        func.count(models.Manifest.id).label("manifest_count"),
        func.count(models.Passenger.id).label("passenger_count")
    ).outerjoin(models.Passenger).filter(
        models.Manifest.arrival_date >= thirty_days_ago.strftime('%Y-%m-%d')
    ).group_by(models.Manifest.arrival_date).order_by(models.Manifest.arrival_date).all()

    # Buat rentang tanggal 30 hari penuh untuk memastikan tidak ada hari yang terlewat
    date_range = pd.to_datetime(pd.date_range(start=thirty_days_ago, end=datetime.now().date()))
    traffic_df = pd.DataFrame(manifests_query, columns=['date', 'manifest_count', 'passenger_count'])
    traffic_df['date'] = pd.to_datetime(traffic_df['date'])
    
    # Gabungkan dengan rentang tanggal penuh
    traffic_df = traffic_df.set_index('date').reindex(date_range, fill_value=0).reset_index()
    traffic_df = traffic_df.rename(columns={'index': 'date'})

    daily_traffic_stats = [
        schemas.DailyTrafficStat(
            date=row.date.strftime('%Y-%m-%d'),
            manifest_count=row.manifest_count,
            passenger_count=row.passenger_count
        ) for row in traffic_df.itertuples()
    ]
    
    # --- 2. Perbandingan Rute ---
    route_query = db.query(
        models.Manifest.destination,
        func.count(models.Passenger.id).label("passenger_count")
    ).outerjoin(models.Passenger).group_by(models.Manifest.destination).all()
    
    route_comparison_stats = [
        schemas.RouteComparisonStat(route=dest, passenger_count=count)
        for dest, count in route_query
    ]
    
    # --- 3. Distribusi Kebangsaan ---
    nationality_query = db.query(
        models.Passenger.nationality,
        func.count(models.Passenger.id).label("count")
    ).group_by(models.Passenger.nationality).order_by(func.count(models.Passenger.id).desc()).all()
    
    nationality_distribution_stats = [
        schemas.NationalityDistributionStat(nationality=nat, count=count)
        for nat, count in nationality_query
    ]

    # --- 4. Distribusi Usia dan Gender ---
    today = datetime.now().date()
    age_groups = {
        "0-17": (0, 17),
        "18-30": (18, 30),
        "31-50": (31, 50),
        "51+": (51, 150) # Rentang atas yang besar
    }
    
    age_gender_distribution = []
    for group_name, (min_age, max_age) in age_groups.items():
        min_dob = today.replace(year=today.year - max_age)
        max_dob = today.replace(year=today.year - min_age)

        q = db.query(
            func.sum(case((models.Passenger.sex == 'M', 1), else_=0)).label('male_count'),
            func.sum(case((models.Passenger.sex == 'F', 1), else_=0)).label('female_count')
        ).filter(models.Passenger.dob.between(min_dob, max_dob)).first()
        
        age_gender_distribution.append(schemas.AgeGenderDistributionStat(
            age_group=group_name,
            male_count=q.male_count or 0,
            female_count=q.female_count or 0
        ))
        
    return schemas.EnhancedDashboardStats(
        daily_traffic=daily_traffic_stats,
        route_comparison=route_comparison_stats,
        nationality_distribution=nationality_distribution_stats,
        age_gender_distribution=age_gender_distribution
    )

# --- ADD THIS NEW FUNCTION TO THE END OF THE FILE ---
def get_dashboard_stats(db: Session):
    # 1. Get total counts
    total_manifests = db.query(models.Manifest).count()
    total_passengers = db.query(models.Passenger).count()

    # 2. Get gender breakdown counts
    male_passengers = db.query(models.Passenger).filter(models.Passenger.sex == "M").count()
    female_passengers = db.query(models.Passenger).filter(models.Passenger.sex == "F").count()

    # 3. Calculate average (handle division by zero if no manifests)
    if total_manifests > 0:
        avg_passengers = round(total_passengers / total_manifests, 1)
    else:
        avg_passengers = 0.0

    # 4. Get the most common nationality
    top_nat_query = db.query(
        models.Passenger.nationality, 
        func.count(models.Passenger.nationality).label("count")
    ).group_by(
        models.Passenger.nationality
    ).order_by(
        func.count(models.Passenger.nationality).desc()
    ).first()

    if top_nat_query:
        top_nationality = schemas.TopNationalityStat(
            nationality=top_nat_query.nationality, 
            count=top_nat_query.count
        )
    else:
        top_nationality = schemas.TopNationalityStat(nationality="N/A", count=0)


    # 5. Return the compiled data in the shape of our Pydantic schema
    return schemas.DashboardStats(
        total_manifests=total_manifests,
        total_passengers=total_passengers,
        male_passengers=male_passengers,
        female_passengers=female_passengers,
        avg_passengers_per_manifest=avg_passengers,
        top_nationality=top_nationality
    )

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedback(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()

def get_manifests(db: Session):
    """(Best Practice) Mengambil semua manifest dengan eager loading dan konversi manual."""
    db_manifests = db.query(models.Manifest).options(
        selectinload(models.Manifest.passengers),
        selectinload(models.Manifest.crews)
    ).order_by(models.Manifest.id.desc()).all()
    
    # Konversi manual setiap objek ke skema Pydantic
    return [schemas.Manifest.from_orm(m) for m in db_manifests]

def get_recent_manifests(db: Session, limit: int = 5):
    """(Best Practice) Mengambil manifest terbaru dengan eager loading dan konversi manual."""
    db_manifests = db.query(models.Manifest).options(
        selectinload(models.Manifest.passengers),
        selectinload(models.Manifest.crews)
    ).order_by(models.Manifest.id.desc()).limit(limit).all()
    
    # Konversi manual setiap objek ke skema Pydantic
    return [schemas.Manifest.from_orm(m) for m in db_manifests]

def get_operational_dashboard_stats(db: Session):
    """Mengambil semua data untuk dasbor operasional."""
    today = date.today()
    
    # 1. Statistik Hari Ini
    arrivals_today = db.query(models.Manifest).filter(
        models.Manifest.destination == OUR_PORT_NAME,
        func.date(models.Manifest.arrival_date) == today
    ).count()

    # --- BARIS YANG HILANG KEMUNGKINAN BESAR ADA DI SINI ---
    departures_today = db.query(models.Manifest).filter(
        models.Manifest.origin == OUR_PORT_NAME,
        func.date(models.Manifest.departure_date) == today
    ).count()
    # ----------------------------------------------------

    passengers_today_arrival = db.query(func.count(models.Passenger.id)).join(models.Manifest).filter(
        models.Manifest.destination == OUR_PORT_NAME,
        func.date(models.Manifest.arrival_date) == today
    ).scalar() or 0
    
    passengers_today_departure = db.query(func.count(models.Passenger.id)).join(models.Manifest).filter(
        models.Manifest.origin == OUR_PORT_NAME,
        func.date(models.Manifest.departure_date) == today
    ).scalar() or 0

    total_passengers_today = passengers_today_arrival + passengers_today_departure

    # 2. Kejadian Berikutnya
    next_arrival_q = db.query(models.Manifest).filter(
        models.Manifest.destination == OUR_PORT_NAME,
        func.date(models.Manifest.arrival_date) >= today
    ).order_by(models.Manifest.arrival_date.asc()).first()

    next_departure_q = db.query(models.Manifest).filter(
        models.Manifest.origin == OUR_PORT_NAME,
        func.date(models.Manifest.departure_date) >= today
    ).order_by(models.Manifest.departure_date.asc()).first()

    next_arrival = schemas.NextShipInfo(
        ship_name=next_arrival_q.ship_name if next_arrival_q else "N/A",
        port=next_arrival_q.origin if next_arrival_q else "N/A",
        time=next_arrival_q.arrival_date if next_arrival_q else None,
    )
    next_departure = schemas.NextShipInfo(
        ship_name=next_departure_q.ship_name if next_departure_q else "N/A",
        port=next_departure_q.destination if next_departure_q else "N/A",
        time=next_departure_q.departure_date if next_departure_q else None,
    )

    # 3. Tren Penumpang 7 Hari
    seven_days_ago = today - timedelta(days=6)
    passenger_trend_q = db.query(
        func.date(models.Manifest.arrival_date).label("date"),
        func.count(case((models.Manifest.destination == OUR_PORT_NAME, models.Passenger.id), else_=None)).label("arrivals"),
        func.count(case((models.Manifest.origin == OUR_PORT_NAME, models.Passenger.id), else_=None)).label("departures")
    ).outerjoin(models.Manifest.passengers).filter(
        func.date(models.Manifest.arrival_date) >= seven_days_ago
    ).group_by(func.date(models.Manifest.arrival_date)).order_by(func.date(models.Manifest.arrival_date).asc()).all()

    trend_map = {item.date.strftime("%Y-%m-%d"): item for item in passenger_trend_q}
    passenger_trend = []
    for i in range(7):
        current_date = seven_days_ago + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        data = trend_map.get(date_str)
        passenger_trend.append(schemas.DailyPassengerTrend(
            date=date_str,
            arrivals=data.arrivals if data else 0,
            departures=data.departures if data else 0,
        ))

    return schemas.DashboardOperationalStats(
        arrivals_today=arrivals_today,
        departures_today=departures_today,
        total_passengers_today=total_passengers_today,
        next_arrival=next_arrival,
        next_departure=next_departure,
        passenger_trend=passenger_trend,
    )
def get_combined_dashboard_stats(db: Session):
    """Mengambil dan menggabungkan data untuk dasbor operasional dan analitik."""
    operational_data = get_operational_dashboard_stats(db)
    analytical_data = get_enhanced_dashboard_stats(db)
    
    return schemas.CombinedDashboardStats(
        operational_stats=operational_data,
        analytical_stats=analytical_data
    )

def get_manifests_by_type(db: Session, manifest_type: str, search: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """Mengambil daftar manifest berdasarkan tipe (kedatangan/keberangkatan) dan filter lainnya."""
    query = db.query(models.Manifest).options(
        selectinload(models.Manifest.passengers),
        selectinload(models.Manifest.crews)
    )

    if manifest_type == "kedatangan":
        query = query.filter(models.Manifest.destination == OUR_PORT_NAME).order_by(models.Manifest.arrival_date.desc())
    elif manifest_type == "keberangkatan":
        query = query.filter(models.Manifest.origin == OUR_PORT_NAME).order_by(models.Manifest.departure_date.desc())
    else:
        return [] # Tipe tidak valid

    if search:
        query = query.filter(models.Manifest.ship_name.ilike(f"%{search}%"))
    if start_date:
        query = query.filter(func.date(models.Manifest.arrival_date if manifest_type == 'kedatangan' else models.Manifest.departure_date) >= start_date)
    if end_date:
        query = query.filter(func.date(models.Manifest.arrival_date if manifest_type == 'kedatangan' else models.Manifest.departure_date) <= end_date)

    return [schemas.Manifest.from_orm(m) for m in query.all()]