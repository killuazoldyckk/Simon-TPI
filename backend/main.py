from __future__ import annotations

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import ValidationError

import crud
import models
from .schemas import LoginRequest
from database import engine, SessionLocal

# Buat tabel di database jika belum ada
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Konfigurasi Keamanan dan Autentikasi JWT ---
SECRET_KEY = os.getenv("SECRET_KEY", "ganti-dengan-kunci-rahasia-yang-sangat-aman-di-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# Event yang berjalan saat aplikasi pertama kali dimulai
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Cek apakah sudah ada pengguna di database
        user = db.query(models.User).first()
        if user is None:
            print("Database pengguna kosong, membuat admin default...")
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

# Dependency untuk menyediakan sesi database ke setiap endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Fungsi-fungsi untuk Autentikasi dan Otorisasi ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Akses ditolak: Hanya untuk admin")
    return current_user

def get_current_agen_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != 'agen':
        raise HTTPException(status_code=403, detail="Akses ditolak: Hanya untuk agen")
    return current_user

# ====================
# API ENDPOINTS
# ====================
@app.post("/api/login")
def login(credentials: LoginRequest):
    email = credentials.email
    password = credentials.password

    user = fake_users.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # **LOGIKA BARU:** Buat token yang berisi email pengguna
    token = f"fake-jwt-token-for-{email}"
        
    return {"token": token, "role": user["role"]}
    
# ====================
# Upload & Parse Manifest
# ====================
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
    # ----------------------------
    db: Session = Depends(get_db),
    # auth: bool = Depends(verify_token)
    email: str = Depends(get_current_user_email)
):
    # --- TAMBAHKAN BLOK PEMERIKSAAN PERAN DI SINI ---
    current_user = fake_users.get(email)
    if not current_user or current_user['role'] != 'agen':
        raise HTTPException(status_code=403, detail="Hanya agen yang dapat mengunggah manifes")
    # --------------------------------------------
    
    # file_location = f"./uploads/{file.filename}"
    os.makedirs("./uploads", exist_ok=True)

    # Simpan kedua file
    passenger_file_location = f"./uploads/{passenger_file.filename}"
    with open(passenger_file_location, "wb") as f:
        f.write(await passenger_file.read())
        
    crew_file_location = f"./uploads/{crew_file.filename}"
    with open(crew_file_location, "wb") as f:
        f.write(await crew_file.read())

   # --- ADDED GLOBAL TRY/EXCEPT BLOCK ---
    try:
        # The sheet name is now "FORMAT_ MANIFEST"
        df_passengers = pd.read_excel(passenger_file_location, sheet_name=0)
        df_passengers = df_passengers.replace({np.nan: None})

        # --- TAMBAHAN: Membersihkan nama kolom dari spasi ---
        df_passengers.columns = df_passengers.columns.str.strip()
        
        # --- TAMBAHAN: Cetak nama kolom untuk debugging ---
        print("Nama kolom penumpang yang terdeteksi:", df_passengers.columns.tolist())


        passengers = []
        # Use index for better error logging
        for index, row in df_passengers.iterrows():
             # --- TAMBAHAN: Lewati baris jika nama penumpang kosong ---
            passenger_name = row.get("HEADER NAME PASSENGER")
            if not passenger_name or pd.isna(passenger_name):
                continue  # Lanjut ke baris berikutnya

            dob = None
            # The date column is now "DATE OF BIRTH \n(DD/MM/YYYY)"
            if "DATE OF BIRTH \n(DD/MM/YYYY)" in row and row["DATE OF BIRTH \n(DD/MM/YYYY)"] is not None:
                try:
                    if isinstance(row["DATE OF BIRTH \n(DD/MM/YYYY)"], (datetime, pd.Timestamp)):
                        dob = row["DATE OF BIRTH \n(DD/MM/YYYY)"].date()
                    else:
                        # The date format is now DD/MM/YYYY
                        dob = pd.to_datetime(
                            row["DATE OF BIRTH \n(DD/MM/YYYY)"], format='%d/%m/%Y').date()
                except Exception as e:
                    # Log the date parse error but don't crash
                    print(
                        f"Warning: Could not parse D.O.B at Excel row {index + 2}: {e}")
                    dob = None

            # Validate each row with the Pydantic schema
            # This will fail cleanly if a required field (like name or passport) is missing
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

        # --- PROSES CREW LIST ---
        # --- LOGIKA BARU UNTUK MEMPROSES CREW LIST ---
        # 1. Tentukan header kustom
        custom_headers = ["No", "Nama", "Tanggal Lahir", "Buku Pelaut", "Masa Berlaku", "Jabatan"]

        # 2. Baca file Excel
        df_crew = pd.read_excel(
            crew_file_location,
            sheet_name="Form 22",
            header=None, # Tidak menggunakan header dari file
            skiprows=17, # Lewati 17 baris pertama, mulai dari baris 18
            usecols=[0, 1, 3, 5, 6, 7] # Pilih kolom 1, 2, 4, 6, 7, 8
        )

        # 3. Tetapkan header kustom ke DataFrame
        df_crew.columns = custom_headers
        df_crew = df_crew.replace({np.nan: None})

        crews = []
        for index, row in df_crew.iterrows():
            # 4. Berhenti jika kolom 'No' kosong
            if pd.isna(row.get('No')):
                break
                
            dob_crew = None
            expiry_crew = None
            
            # Konversi tanggal lahir
            if pd.notna(row.get('Tanggal Lahir')):
                try:
                    # Cek jika formatnya sudah tanggal
                    if isinstance(row.get('Tanggal Lahir'), (datetime, pd.Timestamp)):
                         dob_crew = row.get('Tanggal Lahir').date()
                    else: # Jika tidak, asumsikan format angka serial Excel
                         dob_crew = (datetime(1900, 1, 1) + pd.to_timedelta(int(row.get('Tanggal Lahir')) - 2, unit='d')).date()
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse Crew D.O.B at Excel row {index + 18}: {e}")

            # Konversi tanggal masa berlaku
            if pd.notna(row.get('Masa Berlaku')):
                try:
                    if isinstance(row.get('Masa Berlaku'), (datetime, pd.Timestamp)):
                         expiry_crew = row.get('Masa Berlaku').date()
                    else:
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

        # Create the Pydantic schema from the form fields
        manifest_data = schemas.ManifestCreate(
            ship_name=ship_name,
            arrival_date=arrival_date,
            origin=origin,
            destination=destination,
            flag=flag,
            skipper_name=skipper_name,
            departure_date=departure_date,
            passengers=passengers,
            crews=crews  # NEW LINE TO ADD CREW DATA
        )

        manifest = crud.create_manifest(db=db, manifest=manifest_data)
        return manifest

    except ValidationError as e:
        # If Pydantic fails (e.g., a 'name' is missing), return a clean 422 error
        raise HTTPException(
            status_code=422, detail=f"Data validation error in Excel file: {str(e)}")
    
    except Exception as e:
        # Catch all other errors (e.g., "FORMAT_ MANIFEST" not found, file corrupt, etc.)
        # Log the full error to your server console
        print(f"Unhandled error during upload: {e}")
        raise HTTPException(
            status_code=500, detail=f"An internal server error occurred: {str(e)}")
    # -------------------------------------

# Analytics Endpoint
# ====================
@app.get("/api/analytics/overview", response_model=schemas.DashboardStats)
def get_analytics_overview(
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
):
    """
    Get high-level statistics for the dashboard overview page.
    """
    return crud.get_dashboard_stats(db)

# ====================
# List & Detail Manifests
# ====================
@app.get("/api/manifests", response_model=list[schemas.Manifest])
def list_manifests(
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
):
    return crud.get_manifests(db)

@app.get("/api/manifests/{manifest_id}", response_model=schemas.Manifest)
def read_manifest(
    manifest_id: int,
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
):
    manifest = crud.get_manifest(db, manifest_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest

@app.post("/api/survey", response_model=schemas.Feedback)
def submit_survey(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
):
    return crud.create_feedback(db=db, feedback=feedback)

@app.get("/api/feedback", response_model=list[schemas.Feedback])
def get_all_feedback(
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token) # Di aplikasi nyata, Anda akan memeriksa peran admin di sini
):
    return crud.get_feedback(db)

# ====================
# Profile Endpoints
# ====================
@app.get("/api/profile")
def get_profile(
    email: str = Depends(get_current_user_email)
):
    user = fake_users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"name": user["name"], "role": user["role"], "photo_url": user["photo_url"], "email": email}

@app.put("/api/profile")
def update_profile(
    profile_data: schemas.ProfileUpdate,
    email: str = Depends(get_current_user_email)
):
    user = fake_users.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["name"] = profile_data.name
    return {"message": "Profil berhasil diperbarui!"}

# ====================
# User Management Endpoint (Admin Only)
# ====================
@app.post("/api/users")
async def create_user(
    # UBAH UNTUK MENERIMA FORM-DATA DAN FILE
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_email: str = Depends(get_current_user_email)
):
    admin_user = fake_users.get(current_user_email)
    if not admin_user or admin_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to create users")
        
    if email in fake_users:
        raise HTTPException(status_code=400, detail="Email already registered")

    # **FIXED FILE PATH:** Save to the shared volume inside the backend container
    save_dir = "/app/shared_assets"
    os.makedirs(save_dir, exist_ok=True)
    # Create the full, correct file path.
    file_path = os.path.join(save_dir, photo.filename)
    with open(file_path, "wb") as f:
        f.write(await photo.read())

    print(f"Admin '{current_user_email}' created a new user: {name} ({email})")

    # The URL path for the frontend is now inside 'user_images'
    photo_url = f"user_images/{photo.filename}"
    
    # Tambahkan pengguna baru ke data dummy kita
    fake_users[email] = {
        "password": password,
        "role": role,
        "name": name,
        "photo_url": photo_url  # Simpan nama file
    }

    return {"message": f"User {name} created successfully."}

# Endpoint baru untuk mendapatkan semua pengguna
@app.get("/api/users", response_model=List[schemas.UserInfo])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    """
    Mengambil daftar semua pengguna dari database. Hanya bisa diakses oleh admin.
    """
    # Panggil fungsi dari crud.py untuk mendapatkan data
    users = crud.get_users(db)
    return users

# --- TAMBAHKAN ENDPOINT BARU DI SINI ---
@app.put("/api/crews/{crew_id}", response_model=schemas.Crew)
def update_crew(
    crew_id: int,
    crew_data: schemas.CrewUpdate,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email)
):
    current_user = fake_users.get(email)
    if not current_user or current_user['role'] != 'agen':
        raise HTTPException(
            status_code=403, detail="Hanya agen yang dapat memperbarui data")
            
    updated_crew = crud.update_crew_details(db, crew_id=crew_id, crew_data=crew_data)
    if updated_crew is None:
        raise HTTPException(status_code=404, detail="Data awak kapal tidak ditemukan")
    return updated_crew
# ----------------------------------------

# --- TAMBAHKAN ENDPOINT BARU UNTUK DASBOR ANALITIK ---
@app.get("/api/analytics/enhanced_dashboard", response_model=schemas.EnhancedDashboardStats)
def get_enhanced_dashboard(
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
):
    return crud.get_enhanced_dashboard_stats(db)
# ----------------------------------------------------