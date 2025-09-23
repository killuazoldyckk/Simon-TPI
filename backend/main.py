from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header, Form
from sqlalchemy.orm import Session
from models import Manifest, Passenger  # import your SQLAlchemy models directly
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

# # ====================
# # Dummy Auth Verification Dependency
# # ====================
# async def verify_token(authorization: str = Header(None)):
#     if authorization is None:
#         raise HTTPException(
#             status_code=401, 
#             detail="Authorization header missing"
#         )
    
#     # In a real app, you would decode a JWT. 
#     # Here, we just check if the token matches our fake one.
#     # A real client would send "Bearer fake-jwt-token". We'll check for both.
    
#     token = authorization
#     if authorization.startswith("Bearer "):
#         token = authorization.split(" ")[1]

#     if token != "fake-jwt-token":
#         raise HTTPException(
#             status_code=401, 
#             detail="Invalid or expired token"
#         )
    
#     return True

# def get_current_user_email(authorization: str = Header(None)):
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
#     token = authorization.split(" ")[1]
    
#     # Simple logic to map our dummy tokens to users
#     if "admin" in token or token == "fake-jwt-token-admin":
#          # A simple way to differentiate tokens if needed
#         user_email = "admin@example.com"
#     else:
#         user_email = "agen@example.com"
    
#     if user_email not in fake_users:
#         raise HTTPException(status_code=401, detail="Invalid token")
        
#     return user_email

# =======================================
# DEPENDENCY FUNCTIONS (DEFINED FIRST)
# =======================================

async def verify_token(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization

    # Check if the token is one of our valid dummy tokens
    if token not in ["fake-jwt-token", "fake-jwt-token-admin"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return True

def get_current_user_email(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
    token = authorization.split(" ")[1]
    
    # **FIXED LOGIC:** Correctly map tokens to user emails
    if token == "fake-jwt-token-admin":
        user_email = "admin@example.com"
    elif token == "fake-jwt-token":
        user_email = "agen@example.com"
    else:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    if user_email not in fake_users:
        raise HTTPException(status_code=404, detail="User not found for this token")
        
    return user_email

@app.post("/api/login")
def login(credentials: LoginRequest):
    email = credentials.email
    password = credentials.password

    user = fake_users.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": "fake-jwt-token", "role": user["role"]}

    # **FIX:** Ensure the correct token is always returned for each role
    token = "fake-jwt-token-admin" if user["role"] == "admin" else "fake-jwt-token"
    return {"token": token, "role": user["role"]}

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
    # ----------------------------
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
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
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email)
):
    # In a real app, you would check if the current user (from email) is an admin
    admin_user = fake_users.get(email)
    if not admin_user or admin_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to create users")

    # For this demo, we just print the new user. In a real app, you'd save it.
    print(f"Admin '{email}' created a new user: {user.model_dump()}")
    
    # Add the new user to our fake database for the demo session
    fake_users[user.email] = {
        "password": user.password,
        "role": user.role,
        "name": user.name,
        "photo_url": "agent-placeholder.png" # Default photo for new users
    }

    return {"message": f"User {user.name} created successfully."}

