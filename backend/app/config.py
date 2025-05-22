import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_key: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # SendGrid
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    from_email: str = os.getenv("FROM_EMAIL", "noreply@carnaval-oruro.com")
    
    # Storage
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", 5242880))  # 5MB
    allowed_extensions: List[str] = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png").split(",")
    
    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:4321",  # Astro dev
        "http://localhost:3000",
        "https://tu-dominio.com"  # Producción
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()