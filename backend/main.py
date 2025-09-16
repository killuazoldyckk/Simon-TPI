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
# Dummy Auth
# ====================
fake_users = {
    "agen@example.com": {"password": "1234", "role": "agen"}
}

@app.post("/api/login")
def login(credentials: LoginRequest):
    email = credentials.email
    password = credentials.password

    user = fake_users.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": "fake-jwt-token", "role": user["role"]}

# ====================
# Dummy Auth Verification Dependency
# ====================
async def verify_token(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(
            status_code=401, 
            detail="Authorization header missing"
        )
    
    # In a real app, you would decode a JWT. 
    # Here, we just check if the token matches our fake one.
    # A real client would send "Bearer fake-jwt-token". We'll check for both.
    
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if token != "fake-jwt-token":
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token"
        )
    
    return True


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
