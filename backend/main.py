# backend/main.py
import os
import io
import json
from datetime import datetime
from typing import List  # <--- PERBAIKAN DI SINI
import pandas as pd
import numpy as np
from pydantic import ValidationError

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header, Form
from sqlalchemy.orm import Session

import crud, models, schemas
from database import engine, SessionLocal
from minio import Minio
from minio.error import S3Error

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "simon-access-key")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "simon-secret-key")
MINIO_BUCKET = "simon-tpi"

# Initialize MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Startup Event to create a default admin user
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        user = db.query(models.User).first()
        if user is None:
            print("Tidak ada pengguna ditemukan, membuat admin default...")
            default_admin = schemas.UserCreate(
                email="admin@example.com",
                password="1234",
                name="Administrator",
                role="admin",
                photo_url="" 
            )
            crud.create_user(db=db, user=default_admin, photo_url=default_admin.photo_url)
            print("Admin default berhasil dibuat dengan email: admin@example.com dan password: 1234")
    finally:
        db.close()

    try:
        found = minio_client.bucket_exists(MINIO_BUCKET)
        if not found:
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"Created bucket '{MINIO_BUCKET}'")
        else:
            print(f"Bucket '{MINIO_BUCKET}' already exists")

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{MINIO_BUCKET}/*"],
                },
            ],
        }
        minio_client.set_bucket_policy(MINIO_BUCKET, json.dumps(policy))
        print(f"Public read policy set for bucket '{MINIO_BUCKET}'")
    except S3Error as exc:
        print("Error setting up MinIO bucket:", exc)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTH DEPENDENCIES ---
def get_current_user(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    if not token.startswith("fake-jwt-token-for-"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    try:
        user_email = token.split("fake-jwt-token-for-")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid token content")
        
    user = crud.get_user_by_email(db, email=user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def get_current_agen_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != 'agen':
        raise HTTPException(status_code=403, detail="Agen access required")
    return current_user


# --- API ENDPOINTS ---
@app.post("/api/login")
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=credentials.email)
    if not user or not crud.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = f"fake-jwt-token-for-{user.email}"
    return {"token": token, "role": user.role}

@app.post("/api/manifests/upload", response_model=schemas.Manifest)
async def upload_manifest(
    passenger_file: UploadFile = File(...),
    crew_file: UploadFile = File(...),
    ship_name: str = Form(...),
    flag: str = Form(...),
    skipper_name: str = Form(...),
    arrival_date: str = Form(...),
    departure_date: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_agen_user)
):
    os.makedirs("./uploads", exist_ok=True)
    passenger_file_location = f"./uploads/{passenger_file.filename}"
    with open(passenger_file_location, "wb") as f:
        f.write(await passenger_file.read())
        
    crew_file_location = f"./uploads/{crew_file.filename}"
    with open(crew_file_location, "wb") as f:
        f.write(await crew_file.read())

    try:
        df_passengers = pd.read_excel(passenger_file_location, sheet_name="FORMAT_ MANIFEST")
        df_passengers = df_passengers.replace({np.nan: None})

        passengers = []
        for index, row in df_passengers.iterrows():
            dob = None
            if "DATE OF BIRTH \n(DD/MM/YYYY)" in row and row["DATE OF BIRTH \n(DD/MM/YYYY)"] is not None:
                try:
                    dob = pd.to_datetime(row["DATE OF BIRTH \n(DD/MM/YYYY)"], format='%d/%m/%Y').date()
                except Exception as e:
                    print(f"Warning: Could not parse D.O.B at Excel row {index + 2}: {e}")

            passenger_data = schemas.PassengerCreate(
                name=row.get("HEADER NAME PASSENGER"),
                sex=row.get("GENDER"),
                birth_place=row.get("PLACE OF BIRTH"),
                dob=dob,
                nationality=row.get("NATIONALITY"),
                passport_no=row.get("PASSPORT NO."),
                remarks=row.get("REMARKS"),
            )
            passengers.append(passenger_data)

        custom_headers = ["No", "Nama", "Tanggal Lahir", "Buku Pelaut", "Masa Berlaku", "Jabatan"]
        df_crew = pd.read_excel(crew_file_location, sheet_name="Form 22", header=None, skiprows=17, usecols=[0, 1, 3, 5, 6, 7])
        df_crew.columns = custom_headers
        df_crew = df_crew.replace({np.nan: None})

        crews = []
        for index, row in df_crew.iterrows():
            if pd.isna(row.get('No')):
                break
            dob_crew, expiry_crew = None, None
            if pd.notna(row.get('Tanggal Lahir')):
                try:
                    dob_crew = (datetime(1900, 1, 1) + pd.to_timedelta(int(row.get('Tanggal Lahir')) - 2, unit='d')).date()
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse Crew D.O.B at Excel row {index + 18}: {e}")
            if pd.notna(row.get('Masa Berlaku')):
                try:
                    expiry_crew = (datetime(1900, 1, 1) + pd.to_timedelta(int(row.get('Masa Berlaku')) - 2, unit='d')).date()
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse Crew Expiry Date at Excel row {index + 18}: {e}")

            crews.append(schemas.CrewCreate(
                name=row.get("Nama"),
                dob=dob_crew,
                seaman_book_no=row.get("Buku Pelaut"),
                seaman_book_expiry=expiry_crew,
                rank=row.get("Jabatan"),
            ))

        manifest_data = schemas.ManifestCreate(
            ship_name=ship_name, arrival_date=arrival_date, origin=origin,
            destination=destination, flag=flag, skipper_name=skipper_name,
            departure_date=departure_date, passengers=passengers, crews=crews
        )
        return crud.create_manifest(db=db, manifest=manifest_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Data validation error in Excel file: {e}")
    except Exception as e:
        print(f"Unhandled error during upload: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/api/manifests", response_model=List[schemas.Manifest])
def list_manifests(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_manifests(db)

@app.get("/api/manifests/{manifest_id}", response_model=schemas.Manifest)
def read_manifest(manifest_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    manifest = crud.get_manifest(db, manifest_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest

@app.put("/api/crews/{crew_id}", response_model=schemas.Crew)
def update_crew(
    crew_id: int,
    crew_data: schemas.CrewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_agen_user)
):
    updated_crew = crud.update_crew_details(db, crew_id=crew_id, crew_data=crew_data)
    if updated_crew is None:
        raise HTTPException(status_code=404, detail="Data awak kapal tidak ditemukan")
    return updated_crew

@app.get("/api/analytics/overview", response_model=schemas.DashboardStats)
def get_analytics_overview(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_dashboard_stats(db)

@app.get("/api/analytics/enhanced_dashboard", response_model=schemas.EnhancedDashboardStats)
def get_enhanced_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_enhanced_dashboard_stats(db)

@app.post("/api/survey", response_model=schemas.Feedback)
def submit_survey(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_feedback(db=db, feedback=feedback)

@app.get("/api/feedback", response_model=List[schemas.Feedback])
def get_all_feedback(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.get_feedback(db)

@app.get("/api/profile", response_model=schemas.User)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/api/profile", response_model=schemas.User)
def update_profile(
    profile_data: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    current_user.name = profile_data.name
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/api/users", response_model=schemas.User)
async def create_user(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        file_content = await photo.read()
        minio_client.put_object(
            MINIO_BUCKET,
            photo.filename,
            io.BytesIO(file_content),
            len(file_content),
            content_type=photo.content_type
        )
        photo_url = f"http://localhost/minio/{MINIO_BUCKET}/{photo.filename}"
    except S3Error as exc:
        print("Error uploading to MinIO:", exc)
        raise HTTPException(status_code=500, detail="Could not upload file to storage.")
        
    user_schema = schemas.UserCreate(
        name=name, email=email, password=password, role=role, photo_url=photo_url
    )
    return crud.create_user(db=db, user=user_schema, photo_url=photo_url)

@app.get("/api/users", response_model=List[schemas.UserInfo])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    users = crud.get_users(db)
    return users