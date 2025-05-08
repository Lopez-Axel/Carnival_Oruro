import os
import httpx
from fastapi import Depends, HTTPException, Header
from starlette.status import HTTP_401_UNAUTHORIZED
from dotenv import load_dotenv

load_dotenv()

SUPABASE_AUTH_URL = os.getenv("SUPABASE_AUTH_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")  # Cambiado para usar SUPABASE_API_KEY

async def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
     
    token = authorization.split(" ")[1]
     
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {token}"
    }
     
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SUPABASE_AUTH_URL}/user", headers=headers)
     
    if response.status_code != 200:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
     
    user_data = response.json()
    return user_data