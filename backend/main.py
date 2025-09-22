from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Header, Form
from sqlalchemy.orm import Session
import schemas, models, crud, database
import pandas as pd
from datetime import datetime, timedelta, date
import numpy as np
from pydantic import ValidationError, BaseModel
from typing import List
from jose import JWTError, jwt
import io
import uuid
from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

load_dotenv()

# --- Konfigurasi ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "manifests")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

SECRET_KEY = "your-very-secret-key-please-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- Inisialisasi DB & App ---
models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

# --- Event Startup & Dependency ---
@app.on_event("startup")
def startup_event():
    try:
        found = minio_client.bucket_exists(MINIO_BUCKET_NAME)
        if not found:
            minio_client.make_bucket(MINIO_BUCKET_NAME)
            print(f"Bucket '{MINIO_BUCKET_NAME}' created.")
        else:
            print(f"Bucket '{MINIO_BUCKET_NAME}' already exists.")
    except S3Error as exc:
        print("Error connecting to MinIO:", exc)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FUNGSI AUTENTIKASI BERBASIS DATABASE ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"sub": data.get("email")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), authorization: str = Header(None)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_type, token = authorization.split(" ")
        if token_type.lower() != "bearer":
            raise credentials_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise credentials_exception
        return user
    except (JWTError, ValueError, AttributeError):
        raise credentials_exception

def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user
    return role_checker

# --- ENDPOINT USER ---
@app.post("/api/users/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/api/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=credentials.email)
    if not user or not crud.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

# --- ENDPOINT MANIFEST ---
@app.post("/api/manifests/upload", response_model=schemas.Manifest)
async def upload_manifest(
    ship_name: str = Form(...),
    voyage_date: date = Form(...),
    flag: str = Form(None),
    skipper_name: str = Form(None),
    origin: str = Form(None),
    destination: str = Form(None),
    # arrival_date: str = Form(None),
    # departure_date: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(["agen"]))
):
    contents = await file.read()
    object_name = f"{uuid.uuid4()}-{file.filename}"
    try:
        minio_client.put_object(
            MINIO_BUCKET_NAME, object_name, io.BytesIO(contents), len(contents),
            content_type=file.content_type
        )
        file_url = minio_client.get_presigned_url("GET", MINIO_BUCKET_NAME, object_name)
        df = pd.read_excel(io.BytesIO(contents), sheet_name="Table 1")
        df = df.replace({np.nan: None})
        passengers_data = []
        for index, row in df.iterrows():
            dob = None
            if "D.O.B" in row and row["D.O.B"] is not None:
                try:
                    if isinstance(row["D.O.B"], (datetime, pd.Timestamp)):
                        dob = row["D.O.B"].date()
                    else:
                        dob = pd.to_datetime(row["D.O.B"]).date()
                except Exception: dob = None
            passenger_data = schemas.PassengerCreate(
                name=row.get("NAME"), sex=row.get("SEX"),
                birth_place=row.get("BIRTH PLACE"), dob=dob,
                nationality=row.get("COUNTRY"), passport_no=row.get("PASSPORT"),
                remarks=row.get("REMARKS")
            )
            passengers_data.append(passenger_data)
        manifest_data = schemas.ManifestCreate(
            ship_name=ship_name, voyage_date=voyage_date, flag=flag,
            skipper_name=skipper_name, origin=origin, destination=destination,
            # arrival_date=arrival_date, departure_date=departure_date,
            passengers=passengers_data
        )
        return crud.create_manifest(
            db=db, manifest=manifest_data,
            file_url=file_url, user_id=current_user.id
        )
    except Exception as e:
        print(f"Unhandled error during upload: {e}")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

# --- Sisa Endpoint ---
@app.get("/api/manifests", response_model=list[schemas.Manifest])
def list_manifests(db: Session = Depends(get_db), user: models.User = Depends(require_role(["agen", "imigrasi", "pelabuhan"]))):
    return crud.get_manifests(db)

@app.get("/api/manifests/{manifest_id}", response_model=schemas.Manifest)
def read_manifest(manifest_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_role(["agen", "imigrasi"]))):
    manifest = crud.get_manifest(db, manifest_id)
    if not manifest: raise HTTPException(status_code=404, detail="Manifest not found")
    return manifest

@app.get("/api/analytics/overview", response_model=schemas.DashboardStats)
def get_analytics_overview(db: Session = Depends(get_db), user: models.User = Depends(require_role(["agen", "pelabuhan"]))):
    return crud.get_dashboard_stats(db)

@app.get("/api/manifests/{manifest_id}/download")
def download_manifest_file(manifest_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_role(["agen", "imigrasi"]))):
    manifest = crud.get_manifest(db, manifest_id)
    if not manifest or not manifest.file_url:
        raise HTTPException(status_code=404, detail="File not found")
    object_name = manifest.file_url.split('/')[-1].split('?')[0]
    try:
        presigned_url = minio_client.get_presigned_url("GET", MINIO_BUCKET_NAME, object_name, expires=timedelta(hours=1))
        return {"url": presigned_url}
    except S3Error as exc:
        print(exc)
        raise HTTPException(status_code=500, detail="Could not generate download link.")