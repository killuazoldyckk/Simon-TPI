# backend/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
import models
import schemas

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

def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedback(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()

