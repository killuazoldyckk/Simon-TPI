from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header
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
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    auth: bool = Depends(verify_token)
):
    file_location = f"./uploads/{file.filename}"
    os.makedirs("./uploads", exist_ok=True)

    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        df = pd.read_excel(file_location, sheet_name="Table 1")
        df = df.where(pd.notna(df), None)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file format")

    # Dummy header kapal (karena file manifest contoh tidak ada kolom kapal)
    ship_name = "TBA"
    arrival_date = datetime.now().strftime("%Y-%m-%d")
    origin = "Unknown"
    destination = "Unknown"

    passengers = []
    for _, row in df.iterrows():
        dob = None
        if "D.O.B" in row and not pd.isna(row["D.O.B"]):
            try:
                dob = pd.to_datetime(row["D.O.B"]).date()
            except Exception:
                dob = None

        passengers.append(schemas.PassengerCreate(
            name=row.get("NAME"),
            sex=row.get("SEX"),
            birth_place=row.get("BIRTH PLACE"),
            dob=dob,
            nationality=row.get("COUNTRY"),
            passport_no=row.get("PASSPORT"),
            remarks=row.get("REMARKS"),
        ))

    manifest_data = schemas.ManifestCreate(
        ship_name=ship_name,
        arrival_date=arrival_date,
        origin=origin,
        destination=destination,
        passengers=passengers
    )

    manifest = crud.create_manifest(db=db, manifest=manifest_data)
    return manifest

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
