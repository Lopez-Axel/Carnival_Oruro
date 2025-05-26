from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.database import get_db
from typing import Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_user_id: Optional[str] = Header(None),
    x_user_email: Optional[str] = Header(None),
    x_development_mode: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Obtener usuario actual con fallback para desarrollo
    Prioridad: JWT Token > Headers de desarrollo > Usuario mock
    """
    
    # 1. Intentar autenticación JWT (producción)
    if credentials and credentials.credentials:
        try:
            payload = jwt.decode(
                credentials.credentials, 
                settings.supabase_jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            user_id: str = payload.get("sub")
            
            if user_id:
                async with get_db() as conn:
                    user = await conn.fetchrow(
                        """
                        SELECT id, email, full_name, user_role, is_active, is_verified
                        FROM user_profiles 
                        WHERE id = $1 AND is_active = true
                        """,
                        uuid.UUID(user_id)
                    )
                    
                    if user:
                        return dict(user)
                        
        except JWTError as e:
            logger.warning(f"JWT validation failed: {e}")
        except Exception as e:
            logger.warning(f"Database lookup failed: {e}")
    
    # 2. Modo desarrollo - usar headers si están disponibles
    if x_user_id or x_development_mode == "true":
        logger.info("Using development mode authentication")
        return {
            "id": x_user_id or str(uuid.uuid4()),
            "email": x_user_email or "dev@example.com",
            "full_name": "Usuario de Desarrollo",
            "user_role": "cliente",
            "is_active": True,
            "is_verified": True
        }
    
    # 3. Fallback para testing sin headers (solo en development)
    if hasattr(settings, 'environment') and settings.environment.lower() == "development":
        logger.info("Using fallback development user")
        return {
            "id": str(uuid.uuid4()),
            "email": "test@example.com",
            "full_name": "Usuario de Prueba",
            "user_role": "cliente",
            "is_active": True,
            "is_verified": True
        }
    
    # 4. En producción o cuando no hay fallback, requerir autenticación
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_client(current_user: dict = Depends(get_current_user)):
    """Solo permite acceso a clientes"""
    if current_user.get("user_role") not in ["cliente", None]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden acceder a esta función"
        )
    return current_user

async def get_current_vendor(current_user: dict = Depends(get_current_user)):
    """Solo permite acceso a vendedores"""
    if current_user.get("user_role") not in ["vendedor", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los vendedores pueden acceder a esta función"
        )
    return current_user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Solo permite acceso a administradores"""
    user_role = current_user.get("user_role", "").lower()
    user_email = current_user.get("email", "").lower()
    
    # Lista de emails de admin (con fallback)
    admin_emails = ["admin@carnaval-oruro.com", "soporte.carnaval.oruro@gmail.com"]
    if hasattr(settings, 'admin_emails'):
        admin_emails = [email.lower() for email in settings.admin_emails]
    
    # Verificar si es admin por role o email
    is_admin = (
        user_role in ["administrador", "admin"] or
        user_email in admin_emails
    )
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a esta función"
        )
    return current_user

async def get_current_vendor_or_admin(current_user: dict = Depends(get_current_user)):
    """Permite acceso a vendedores y administradores"""
    user_role = current_user.get("user_role", "").lower()
    
    if user_role not in ["vendedor", "administrador", "admin", "vendor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para vendedores y administradores"
        )
    return current_user