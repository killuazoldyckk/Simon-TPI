from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header, Form
from sqlalchemy.orm import Session
from models import Manifest, Passenger, Crew  # import your SQLAlchemy models directly
import schemas
import models
import crud
import database
import pandas as pd
import os
from datetime import datetime
from schemas import LoginRequest
import numpy as np
from pydantic import ValidationError


# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ====================
# Dummy Auth & User Data
# ====================
fake_users = {
    "agen@example.com": {
        "password": "1234",
        "role": "agen",
        "name": "Agen Kapal",
        "photo_url": "logo_indomal.png"
    },
    "admin@example.com": {
        "password": "1234",
        "role": "admin",
        "name": "Administrator Sistem",
        "photo_url": "logo_Imigrasi.png"
    }
}

# =======================================
# DEPENDENCY FUNCTIONS (DEFINED FIRST)
# =======================================
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.split(" ")[1]

    # **LOGIKA BARU:** Periksa format token
    if not token.startswith("fake-jwt-token-for-"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    return True

def get_current_user_email(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
    token = authorization.split(" ")[1]
    
    # **LOGIKA BARU:** Ekstrak email langsung dari token
    try:
        user_email = token.split("fake-jwt-token-for-")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid token content")
        
    if user_email not in fake_users:
        raise HTTPException(status_code=404, detail="User from token not found")
        
    return user_email

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
        df_passengers = pd.read_excel(passenger_file_location, sheet_name="FORMAT_ MANIFEST")
        df_passengers = df_passengers.replace({np.nan: None})

        passengers = []
        # Use index for better error logging
        for index, row in df_passengers.iterrows():
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
# @app.post("/api/manifests/upload", response_model=schemas.Manifest)
# async def upload_manifest(
#     # --- THIS PART IS ALL NEW ---
#     # We now accept Form data instead of a JSON body
#     file: UploadFile = File(...),
#     ship_name: str = Form(...),
#     flag: str = Form(...),
#     skipper_name: str = Form(...),
#     arrival_date: str = Form(...),
#     departure_date: str = Form(...),
#     origin: str = Form(...),
#     destination: str = Form(...),
#     # ----------------------------
#     db: Session = Depends(get_db),
#     # auth: bool = Depends(verify_token)
#     email: str = Depends(get_current_user_email)
# ):
#     # --- TAMBAHKAN BLOK PEMERIKSAAN PERAN DI SINI ---
#     current_user = fake_users.get(email)
#     if not current_user or current_user['role'] != 'agen':
#         raise HTTPException(status_code=403, detail="Hanya agen yang dapat mengunggah manifes")
#     # --------------------------------------------
    
#     file_location = f"./uploads/{file.filename}"
#     os.makedirs("./uploads", exist_ok=True)

#     with open(file_location, "wb") as f:
#         f.write(await file.read())

#    # --- ADDED GLOBAL TRY/EXCEPT BLOCK ---
#     try:
#         df = pd.read_excel(file_location, sheet_name="Table 1")
#         df = df.replace(np.nan, None)

#         passengers = []
#         for index, row in df.iterrows():  # Use index for better error logging
#             dob = None
#             if "D.O.B" in row and row["D.O.B"] is not None:
#                 try:
#                     if isinstance(row["D.O.B"], (datetime, pd.Timestamp)):
#                         dob = row["D.O.B"].date()
#                     else:
#                         dob = pd.to_datetime(row["D.O.B"]).date()
#                 except Exception as e:
#                     # Log the date parse error but don't crash
#                     print(f"Warning: Could not parse D.O.B at Excel row {index + 2}: {e}")
#                     dob = None

#             # Validate each row with the Pydantic schema
#             # This will fail cleanly if a required field (like name or passport) is missing
#             passenger_data = schemas.PassengerCreate(
#                 name=row.get("NAME"),
#                 sex=row.get("SEX"),
#                 birth_place=row.get("BIRTH PLACE"),
#                 dob=dob,
#                 nationality=row.get("COUNTRY"),
#                 passport_no=row.get("PASSPORT"),
#                 remarks=row.get("REMARKS"),
#             )
#             passengers.append(passenger_data)

#         # Create the Pydantic schema from the form fields
#         manifest_data = schemas.ManifestCreate(
#             ship_name=ship_name,
#             arrival_date=arrival_date,
#             origin=origin,
#             destination=destination,
#             flag=flag,
#             skipper_name=skipper_name,
#             departure_date=departure_date,
#             passengers=passengers
#         )

#         manifest = crud.create_manifest(db=db, manifest=manifest_data)
#         return manifest

#     except ValidationError as e:
#         # If Pydantic fails (e.g., a 'name' is missing), return a clean 422 error
#         raise HTTPException(status_code=422, detail=f"Data validation error in Excel file: {str(e)}")
    
#     except Exception as e:
#         # Catch all other errors (e.g., "Table 1" not found, file corrupt, etc.)
#         print(f"Unhandled error during upload: {e}") # Log the full error to your server console
#         raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
#     # -------------------------------------

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
@app.get("/api/users", response_model=list[schemas.UserInfo])
def get_users(email: str = Depends(get_current_user_email)):
    admin_user = fake_users.get(email)
    if not admin_user or admin_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat melihat daftar pengguna")
    
    user_list = []
    for user_email, user_data in fake_users.items():
        user_list.append({
            "name": user_data["name"],
            "email": user_email,
            "role": user_data["role"],
            "photo_url": user_data["photo_url"]
        })
    return user_list