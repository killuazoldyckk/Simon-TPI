# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# --- TAMBAHKAN BLOK DEBUG DI SINI ---
print("="*50)
print(f"URL Database yang dibaca dari .env: {SQLALCHEMY_DATABASE_URL}")
print("="*50)
# -----------------------------------

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("Variabel lingkungan DATABASE_URL tidak diatur")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()