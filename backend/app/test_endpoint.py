from fastapi import APIRouter, HTTPException
import os
import httpx
from dotenv import load_dotenv
import json

router = APIRouter()
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_AUTH_URL = os.getenv("SUPABASE_AUTH_URL")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

@router.get("/test-connection")
async def test_connection():
    """
    Prueba la conexión a Supabase usando las variables de entorno configuradas
    """
    env_vars = {
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_API_KEY": SUPABASE_API_KEY[:5] + "..." if SUPABASE_API_KEY else None,
        "SUPABASE_AUTH_URL": SUPABASE_AUTH_URL,
        "SUPABASE_DB_URL": SUPABASE_DB_URL
    }
    
    # Intenta hacer una petición simple a Supabase
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Intentar listar las tablas
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
            response.raise_for_status()
            
            return {
                "status": "connected",
                "environment_variables": env_vars,
                "supabase_tables": response.json()
            }
    except Exception as e:
        return {
            "status": "error",
            "environment_variables": env_vars,
            "error_message": str(e)
        }

@router.post("/test-create-user")
async def test_create_user():
    """
    Intenta crear un usuario de prueba directamente en Supabase
    """
    import time
    import uuid
    
    # Datos de prueba fijos con valores únicos
    test_user = {
        "email": f"test{int(time.time())}@example.com",  # Correo único
        "display_name": "Usuario de Prueba 2",
        "google_id": f"test_{uuid.uuid4()}",  # ID único
        "photo_url": "https://example.com/photo.jpg"
    }
    
    # Headers para la petición
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        # Crear usuario directamente
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/users", 
                headers=headers,
                json=test_user
            )
            
            # Devolver el resultado
            return {
                "status": response.status_code,
                "response": response.json() if response.status_code < 300 else response.text,
                "user_data": test_user
            }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
            "user_data": test_user
        }