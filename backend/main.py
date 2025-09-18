from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header, Form
from sqlalchemy.orm import Session
from models import Manifest, Passenger  # import your SQLAlchemy models directly
import schemas
import models
import crud
import database
import pandas as pd
import os
from datetime import datetime, timedelta
from schemas import LoginRequest
import numpy as np
from pydantic import ValidationError, BaseModel
from typing import List


# --- IMPOR UNTUK JWT ---
from jose import JWTError, jwt

# --- KONFIGURASI JWT ---
# (Dalam aplikasi nyata, INI HARUS DI AMBIL DARI ENVIRONMENT VARIABLES)
SECRET_KEY = "your-very-secret-key-please-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


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
# Dummy Auth
# ====================
# --- PENGGUNA DUMMY DENGAN ROLES ---
fake_users = {
    "agen@example.com": {"password": "1234", "role": "agen"},
    "imigrasi@example.com": {"password": "1234", "role": "imigrasi"},
    "pelabuhan@example.com": {"password": "1234", "role": "pelabuhan"}
}

class TokenData(BaseModel):
    """Skema data di dalam payload JWT."""
    email: str | None = None
    role: str | None = None

def create_access_token(data: dict):
    """Membuat JWT baru berdasarkan data user."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 'sub' (subject) adalah klaim standar JWT untuk user identifier
    to_encode.update({"sub": data.get("email")}) 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- ENDPOINT LOGIN BARU ---
@app.post("/api/login", response_model=schemas.TokenResponse)
def login(credentials: LoginRequest):
    email = credentials.email
    password = credentials.password

    user = fake_users.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Buat token dengan email dan role
    access_token = create_access_token(
        data={"email": email, "role": user["role"]}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user["role"]
    }


# --- DEPENDENCY UNTUK VALIDASI TOKEN (MENGGANTIKAN verify_token) ---
async def get_current_user(authorization: str = Header(None)):
    """
    Memvalidasi token JWT dari header dan mengembalikan payload (data user).
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if authorization is None:
        raise credentials_exception
        
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        email: str = payload.get("sub")
        role: str = payload.get("role")
        
        if email is None or role is None:
            raise credentials_exception
            
        user = fake_users.get(email)
        if user is None or user["role"] != role:
             raise credentials_exception
             
        # Mengembalikan data user yang akan disuntikkan ke endpoint
        return {"email": email, "role": role}

    except (JWTError, ValueError, AttributeError):
        raise credentials_exception

# --- DEPENDENCY FACTORY UNTUK OTORISASI ROLE ---
def require_role(allowed_roles: List[str]):
    """
    Sebuah dependency factory yang membuat dependency baru 
    untuk memeriksa apakah role user diizinkan.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail="Forbidden: You do not have access to this resource."
            )
        return current_user
    
    return role_checker

# ====================
# Upload & Parse Manifest
# ====================
@app.post("/api/manifests/upload", response_model=schemas.Manifest)
async def upload_manifest(
    # --- THIS PART IS ALL NEW ---
    # We now accept Form data instead of a JSON body
    file: UploadFile = File(...),
    ship_name: str = Form(...),
    flag: str = Form(...),
    skipper_name: str = Form(...),
    arrival_date: str = Form(...),
    departure_date: str = Form(...),
    origin: str = Form(...),
    destination: str = Form(...),
    db: Session = Depends(get_db),
    # --- DEPENDENCY DIPERBARUI: Memerlukan role 'agen' ---
    user: dict = Depends(require_role(["agen"]))
):
    file_location = f"./uploads/{file.filename}"
    os.makedirs("./uploads", exist_ok=True)

    with open(file_location, "wb") as f:
        f.write(await file.read())

   # --- ADDED GLOBAL TRY/EXCEPT BLOCK ---
    try:
        df = pd.read_excel(file_location, sheet_name="Table 1")
        df = df.replace(np.nan, None)

        passengers = []
        for index, row in df.iterrows():  # Use index for better error logging
            dob = None
            if "D.O.B" in row and row["D.O.B"] is not None:
                try:
                    if isinstance(row["D.O.B"], (datetime, pd.Timestamp)):
                        dob = row["D.O.B"].date()
                    else:
                        dob = pd.to_datetime(row["D.O.B"]).date()
                except Exception as e:
                    # Log the date parse error but don't crash
                    print(f"Warning: Could not parse D.O.B at Excel row {index + 2}: {e}")
                    dob = None

            # Validate each row with the Pydantic schema
            # This will fail cleanly if a required field (like name or passport) is missing
            passenger_data = schemas.PassengerCreate(
                name=row.get("NAME"),
                sex=row.get("SEX"),
                birth_place=row.get("BIRTH PLACE"),
                dob=dob,
                nationality=row.get("COUNTRY"),
                passport_no=row.get("PASSPORT"),
                remarks=row.get("REMARKS"),
            )
            passengers.append(passenger_data)

        # Create the Pydantic schema from the form fields
        manifest_data = schemas.ManifestCreate(
            ship_name=ship_name,
            arrival_date=arrival_date,
            origin=origin,
            destination=destination,
            flag=flag,
            skipper_name=skipper_name,
            departure_date=departure_date,
            passengers=passengers
        )

        manifest = crud.create_manifest(db=db, manifest=manifest_data)
        return manifest

    except ValidationError as e:
        # If Pydantic fails (e.g., a 'name' is missing), return a clean 422 error
        raise HTTPException(status_code=422, detail=f"Data validation error in Excel file: {str(e)}")
    
    except Exception as e:
        # Catch all other errors (e.g., "Table 1" not found, file corrupt, etc.)
        print(f"Unhandled error during upload: {e}") # Log the full error to your server console
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
    # -------------------------------------

# ====================
# Analytics Endpoint
# BISA DIAKSES OLEH 'agen' dan 'pelabuhan'
# ====================
@app.get("/api/analytics/overview", response_model=schemas.DashboardStats)
def get_analytics_overview(
    db: Session = Depends(get_db),
    # --- DEPENDENCY DIPERBARUI ---
    user: dict = Depends(require_role(["agen", "pelabuhan"]))
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
    # --- DEPENDENCY DIPERBARUI: 'imigrasi' bisa lihat daftar list, 'pelabuhan' juga ---
    user: dict = Depends(require_role(["agen", "imigrasi", "pelabuhan"]))
):
    return crud.get_manifests(db)

@app.get("/api/manifests/{manifest_id}", response_model=schemas.Manifest)
def read_manifest(
    manifest_id: int,
    db: Session = Depends(get_db),
    # --- DEPENDENCY DIPERBARUI: 'imigrasi' bisa lihat detail, 'pelabuhan' juga ---
    user: dict = Depends(require_role(["agen", "imigrasi"," pelabuhan"]))
):
    manifest = crud.get_manifest(db, manifest_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest