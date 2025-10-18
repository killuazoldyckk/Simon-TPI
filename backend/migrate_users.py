# backend/migrate_users.py

import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud

# Perintah ini akan membuat tabel 'users' jika belum ada
models.Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

print("Memulai migrasi pengguna dari users.json ke database...")

try:
    with open('users.json', 'r') as f:
        users_from_json = json.load(f)

    for user_data in users_from_json:
        existing_user = crud.get_user_by_username(db, username=user_data['username'])
        if not existing_user:
            print(f"Membuat pengguna: {user_data['username']}...")
            
            user_schema = schemas.UserCreate(
                name=user_data.get('name', user_data['username']),
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                photo_url=user_data.get('photo_url')
            )
            crud.create_user(db=db, user=user_schema)
        else:
            print(f"Pengguna {user_data['username']} sudah ada, dilewati.")

    print("Migrasi berhasil diselesaikan.")

except FileNotFoundError:
    print("Error: File users.json tidak ditemukan.")
finally:
    db.close()