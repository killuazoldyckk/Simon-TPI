from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

fake_users = {
    "agen@example.com": {"password": "123", "role": "agen"},
    "imigrasi@example.com": {"password": "123", "role": "imigrasi"},
    "admin@example.com": {"password": "123", "role": "admin"},
}

class LoginData(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
def login(data: LoginData):
    user = fake_users.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": "FAKEJWT123", "role": user["role"]}

@app.get("/users/me")
def get_me():
    # Untuk sementara return dummy
    return {"email": "agen@example.com", "role": "agen"}
