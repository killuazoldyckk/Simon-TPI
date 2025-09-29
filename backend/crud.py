# backend/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import models
import schemas

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


def create_manifest(db: Session, manifest: schemas.ManifestCreate):
    
    db_passengers = [
        models.Passenger(**p.model_dump()) for p in manifest.passengers
    ]

    # --- TAMBAHKAN LOGIKA UNTUK CREW ---
    db_crews = [models.Crew(**c.model_dump()) for c in manifest.crews]
    
    db_manifest = models.Manifest(
        ship_name=manifest.ship_name,
        arrival_date=manifest.arrival_date,
        origin=manifest.origin,
        destination=manifest.destination,
        
        # --- ADDED FIELDS ---
        flag=manifest.flag,
        skipper_name=manifest.skipper_name,
        departure_date=manifest.departure_date,
        # --------------------

        passengers=db_passengers,
        crews=db_crews  # NEW LINE TO ADD CREW DATA
    )
    
    db.add(db_manifest)
    db.commit()
    db.refresh(db_manifest)
    return db_manifest

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
    # This query groups passengers by nationality, counts each group,
    # and orders by the count to get the highest one first.
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

def get_manifests(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Manifest)
        .options(
            joinedload(models.Manifest.passengers),
            joinedload(models.Manifest.crews)
            )  # NEW LINE TO LOAD CREW DATA
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_manifest(db: Session, manifest_id: int):
    return (
        db.query(models.Manifest)
        .options(joinedload(models.Manifest.passengers))
        .filter(models.Manifest.id == manifest_id)
        .first()
    )

# --- TAMBAHKAN FUNGSI BARU DI SINI ---
def update_crew_details(db: Session, crew_id: int, crew_data: schemas.CrewUpdate):
    db_crew = db.query(models.Crew).filter(models.Crew.id == crew_id).first()
    if not db_crew:
        return None
    
    update_data = crew_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_crew, key, value)
        
    db.commit()
    db.refresh(db_crew)
    return db_crew
# --------------------------------------

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedback(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()

