# backend/main.py

from __future__ import annotations # HARUS MENJADI BARIS PERTAMA

import os
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Impor absolut dari modul lokal Anda
import crud
import models
import schemas
from database import SessionLocal, engine

# Buat tabel di database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Konfigurasi Keamanan dan Autentikasi JWT ---
SECRET_KEY = os.getenv("SECRET_KEY", "ganti-dengan-kunci-rahasia-yang-sangat-aman-di-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Dependency database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Fungsi-fungsi Autentikasi ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_username(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(username=username)
    if user is None: raise credentials_exception
    return user

def get_current_admin_user(current_user: dict = Depends(get_current_username)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak: Hanya untuk admin")
    return current_user

def get_current_agen_user(current_user: dict = Depends(get_current_username)):
    if current_user.get("role") != "agen":
        raise HTTPException(status_code=403, detail="Akses ditolak: Hanya untuk agen")
    return current_user


# --- ENDPOINTS API ---

@app.post("/api/login")
def login(credentials: schemas.LoginRequest):
    # --- KODE DEBUG DIMULAI ---
    print("="*20, "DEBUG LOGIN", "="*20)
    print(f"Mencoba login dengan username: '{credentials.username}'")

    user = crud.get_user_by_username(username=credentials.username)

    if not user:
        print("HASIL: Pengguna TIDAK ditemukan.")
        print("="*53)
        raise HTTPException(status_code=401, detail="Username atau password salah")
    
    print(f"HASIL: Pengguna ditemukan -> {user}")

    password_cocok = crud.verify_password(credentials.password, user['password'])
    print(f"Mengecek password: '{credentials.password}' vs '{user['password']}' -> Cocok: {password_cocok}")
    print("="*53)
    # --- KODE DEBUG SELESAI ---

    if not password_cocok:
        raise HTTPException(status_code=401, detail="Username atau password salah")
    
    # Jika berhasil, buat token
    access_token = create_access_token(data={"sub": user['username']}) 
    return {"access_token": access_token, "token_type": "bearer", "role": user['role']}

@app.get("/api/users", response_model=List[schemas.UserInfo])
def get_users(current_user: dict = Depends(get_current_admin_user)):
    return crud.get_users()

@app.get("/api/profile", response_model=schemas.UserInfo)
def get_profile(current_user: dict = Depends(get_current_username)):
    return current_user

@app.get("/api/users", response_model=List[schemas.UserInfo])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.get_users(db)


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
    current_user: models.User = Depends(get_current_agen_user),
):
    upload_folder = "storage/manifests"
    os.makedirs(upload_folder, exist_ok=True)
    passenger_file_location = os.path.join(upload_folder, passenger_file.filename)
    with open(passenger_file_location, "wb") as f:
        f.write(await passenger_file.read())
    crew_file_location = os.path.join(upload_folder, crew_file.filename)
    with open(crew_file_location, "wb") as f:
        f.write(await crew_file.read())
    try:
        df_passengers = pd.read_excel(passenger_file_location, sheet_name=0)
        df_passengers = df_passengers.replace({np.nan: None})
        df_passengers.columns = df_passengers.columns.str.strip()
        passengers = []
        for index, row in df_passengers.iterrows():
            passenger_name = row.get("HEADER NAME PASSENGER")
            if not passenger_name or pd.isna(passenger_name):
                continue
            dob = None
            if "DATE OF BIRTH \n(DD/MM/YYYY)" in row and row["DATE OF BIRTH \n(DD/MM/YYYY)"] is not None:
                try:
                    dob = pd.to_datetime(
                        row["DATE OF BIRTH \n(DD/MM/YYYY)"], format="%d/%m/%Y"
                    ).date()
                except Exception as e:
                    print(f"Peringatan: Gagal parse D.O.B Penumpang di baris Excel {index + 2}: {e}")
            passenger_data = schemas.PassengerCreate(
                name=passenger_name,
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
            if pd.isna(row.get("No")):
                break
            dob_crew, expiry_crew = None, None
            if pd.notna(row.get("Tanggal Lahir")):
                try:
                    dob_crew = (datetime(1900, 1, 1) + pd.to_timedelta(int(row.get("Tanggal Lahir")) - 2, unit="d")).date()
                except (ValueError, TypeError) as e:
                    print(f"Peringatan: Gagal parse D.O.B Kru di baris Excel {index + 18}: {e}")
            if pd.notna(row.get("Masa Berlaku")):
                try:
                    expiry_crew = (datetime(1900, 1, 1) + pd.to_timedelta(int(row.get("Masa Berlaku")) - 2, unit="d")).date()
                except (ValueError, TypeError) as e:
                    print(f"Peringatan: Gagal parse Tanggal Berlaku Kru di baris Excel {index + 18}: {e}")
            crews.append(
                schemas.CrewCreate(
                    name=row.get("Nama"),
                    dob=dob_crew,
                    seaman_book_no=row.get("Buku Pelaut"),
                    seaman_book_expiry=expiry_crew,
                    rank=row.get("Jabatan"),
                )
            )
        manifest_data = schemas.ManifestCreate(
            ship_name=ship_name, arrival_date=arrival_date, origin=origin, destination=destination,
            flag=flag, skipper_name=skipper_name, departure_date=departure_date, passengers=passengers, crews=crews,
        )
        return crud.create_manifest(db=db, manifest=manifest_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Error validasi data di file Excel: {e}")
    except Exception as e:
        print(f"Error tidak terduga saat unggah: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {e}")

# ... (Salin sisa endpoint Anda yang lain di sini: /api/manifests, /api/profile, dll.)
@app.get("/api/manifests", response_model=List[schemas.Manifest])
def list_manifests(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_username)):
    return crud.get_manifests(db)


@app.get("/api/manifests/{manifest_id}", response_model=schemas.Manifest)
def read_manifest(manifest_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_username)):
    manifest = crud.get_manifest(db, manifest_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest tidak ditemukan")
    return manifest


@app.put("/api/crews/{crew_id}", response_model=schemas.Crew)
def update_crew(
    crew_id: int,
    crew_data: schemas.CrewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_agen_user),
):
    updated_crew = crud.update_crew_details(db, crew_id=crew_id, crew_data=crew_data)
    if updated_crew is None:
        raise HTTPException(status_code=404, detail="Data awak kapal tidak ditemukan")
    return updated_crew


@app.get("/api/analytics/overview", response_model=schemas.DashboardStats)
def get_analytics_overview(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_username)):
    return crud.get_dashboard_stats(db)


@app.get("/api/analytics/enhanced_dashboard", response_model=schemas.EnhancedDashboardStats)
def get_enhanced_dashboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_username)):
    return crud.get_enhanced_dashboard_stats(db)


@app.post("/api/survey", response_model=schemas.Feedback)
def submit_survey(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_username)):
    return crud.create_feedback(db=db, feedback=feedback)


@app.get("/api/feedback", response_model=List[schemas.Feedback])
def get_all_feedback(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.get_feedback(db)

@app.put("/api/profile", response_model=schemas.User)
def update_profile(
    profile_data: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_username),
):
    current_user.name = profile_data.name
    db.commit()
    db.refresh(current_user)
    return current_user