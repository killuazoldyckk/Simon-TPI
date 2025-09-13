from sqlalchemy.orm import Session, joinedload  # <-- Make sure joinedload is imported
import models
import schemas

def create_manifest(db: Session, manifest: schemas.ManifestCreate):
    
    # 1. Convert all Pydantic passengers into SQLAlchemy models
    db_passengers = [
        models.Passenger(**p.model_dump()) for p in manifest.passengers
    ]
    
    # 2. Create the Manifest model, assigning the list of models
    #    DIRECTLY to the ".passengers" relationship.
    db_manifest = models.Manifest(
        ship_name=manifest.ship_name,
        arrival_date=manifest.arrival_date,
        origin=manifest.origin,
        destination=manifest.destination,
        passengers=db_passengers  # <-- Assign the list here
    )
    
    # 3. Add ONLY the manifest. SQLAlchemy's "cascade" save
    #    will automatically add all the passengers in the list.
    db.add(db_manifest)
    db.commit()
    db.refresh(db_manifest)  # Refresh to get all the new data (like IDs)
    return db_manifest


def get_manifests(db: Session, skip: int = 0, limit: int = 100):
    # This now EAGERLY loads the passenger list to prevent crashes
    return (
        db.query(models.Manifest)
        .options(joinedload(models.Manifest.passengers))  # <-- This is required
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_manifest(db: Session, manifest_id: int):
    # This now EAGERLY loads the passenger list to prevent crashes
    return (
        db.query(models.Manifest)
        .options(joinedload(models.Manifest.passengers))  # <-- This is required
        .filter(models.Manifest.id == manifest_id)
        .first()
    )