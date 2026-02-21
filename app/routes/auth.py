from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from database import get_conn, release_conn
import os

router = APIRouter(prefix="/api/auth")
pwd_ctx = CryptContext(schemes=["bcrypt"])
SECRET = os.environ.get('JWT_SECRET')

@router.post("/register")
def register(email: str, password: str, username: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, username, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (email, username, pwd_ctx.hash(password))
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            return {"user_id": user_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, str(e))
    finally:
        release_conn(conn)

@router.post("/login")
def login(email: str, password: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if not row or not pwd_ctx.verify(password, row[1]):
                raise HTTPException(401, "Invalid credentials")
            token = jwt.encode(
                {"sub": str(row[0]), "exp": datetime.utcnow() + timedelta(hours=1)},
                SECRET, algorithm="HS256"
            )
            return {"token": token}
    finally:
        release_conn(conn)
