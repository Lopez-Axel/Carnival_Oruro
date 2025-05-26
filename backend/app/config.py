import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import logging

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Supabase
    supabase_url: str = Field("", env="SUPABASE_URL")
    supabase_anon_key: str = Field("", env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field("", env="SUPABASE_SERVICE_KEY")
    supabase_jwt_secret: str = Field("", env="SUPABASE_JWT_SECRET")
    
    # SendGrid
    sendgrid_api_key: str = Field("", env="SENDGRID_API_KEY")
    from_email: str = Field("noreply@carnaval-oruro.com", env="FROM_EMAIL")
    
    # Storage - usando string en lugar de List para evitar el error de parsing
    max_upload_size: int = Field(5242880, env="MAX_UPLOAD_SIZE")  # 5MB
    allowed_extensions_str: str = Field("pdf,jpg,jpeg,png", env="ALLOWED_EXTENSIONS")
    storage_bucket_name: str = Field("vendor-documents", env="STORAGE_BUCKET_NAME")
    
    # JWT
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Environment
    environment: str = Field("development", env="ENV")
    
    # Admin emails - usando string para evitar el error de parsing
    admin_emails_str: str = Field("admin@carnaval-oruro.com", env="ADMIN_EMAILS")
    
    # CORS
    frontend_origin: str = Field("http://localhost:4321", env="FRONTEND_ORIGIN")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Convert comma-separated string to list"""
        return [ext.strip().lower() for ext in self.allowed_extensions_str.split(",") if ext.strip()]
    
    @property
    def admin_emails(self) -> List[str]:
        """Convert comma-separated string to list"""
        return [email.strip().lower() for email in self.admin_emails_str.split(",") if email.strip()]
    
    @property
    def allowed_origins(self) -> List[str]:
        """CORS allowed origins"""
        return [
            self.frontend_origin,
            "http://localhost:3000",
            "http://localhost:4321"
        ]

# Crear configuración con manejo de errores robusto
def create_settings():
    try:
        settings = Settings()
        print("✅ Settings loaded successfully")
        print(f"   Environment: {settings.environment}")
        print(f"   Database: {'✅ Connected' if settings.database_url else '❌ Missing'}")
        print(f"   Supabase: {'✅ Configured' if settings.supabase_url else '❌ Missing'}")
        print(f"   SendGrid: {'✅ Configured' if settings.sendgrid_api_key else '❌ Missing'}")
        print(f"   Frontend: {settings.frontend_origin}")
        return settings
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        print("Creating fallback settings...")
        
        # Crear configuración de fallback usando variables de entorno directamente
        class FallbackSettings:
            def __init__(self):
                self.database_url = os.getenv("DATABASE_URL", "")
                self.supabase_url = os.getenv("SUPABASE_URL", "")
                self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
                self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
                self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "dev-secret")
                self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
                self.from_email = os.getenv("FROM_EMAIL", "noreply@carnaval-oruro.com")
                self.max_upload_size = int(os.getenv("MAX_UPLOAD_SIZE", "5242880"))
                self.allowed_extensions_str = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png")
                self.storage_bucket_name = os.getenv("STORAGE_BUCKET_NAME", "vendor-documents")
                self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
                self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
                self.environment = os.getenv("ENV", "development")
                self.admin_emails_str = os.getenv("ADMIN_EMAILS", "admin@carnaval-oruro.com")
                self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:4321")
            
            @property
            def allowed_extensions(self):
                return [ext.strip().lower() for ext in self.allowed_extensions_str.split(",") if ext.strip()]
            
            @property
            def admin_emails(self):
                return [email.strip().lower() for email in self.admin_emails_str.split(",") if email.strip()]
            
            @property
            def allowed_origins(self):
                return [self.frontend_origin, "http://localhost:3000", "http://localhost:4321"]
        
        settings = FallbackSettings()
        print("✅ Fallback settings loaded successfully")
        return settings

# Crear la instancia de settings
settings = create_settings()