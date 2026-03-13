import os
from fastapi import Depends, HTTPException, Header

API_TOKEN = os.getenv("API_TOKEN", "your-secret-token")

async def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")