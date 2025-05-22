from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config import settings
from app.database import get_db
from typing import Optional
import uuid

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Obtener usuario actual desde JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.supabase_jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Obtener datos del usuario desde la base de datos
    async with get_db() as conn:
        user = await conn.fetchrow(
            """
            SELECT id, email, full_name, user_role, is_active, is_verified
            FROM user_profiles 
            WHERE id = $1 AND is_active = true
            """,
            uuid.UUID(user_id)
        )
        
        if user is None:
            raise credentials_exception
            
        return dict(user)

async def get_current_client(current_user: dict = Depends(get_current_user)):
    """Solo permite acceso a clientes"""
    if current_user.get("user_role") != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los clientes pueden acceder a esta función"
        )
    return current_user

async def get_current_vendor(current_user: dict = Depends(get_current_user)):
    """Solo permite acceso a vendedores"""
    if current_user.get("user_role") != "vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los vendedores pueden acceder a esta función"
        )
    return current_user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """Solo permite acceso a administradores"""
    if current_user.get("user_role") != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a esta función"
        )
    return current_user

async def get_current_vendor_or_admin(current_user: dict = Depends(get_current_user)):
    """Permite acceso a vendedores y administradores"""
    if current_user.get("user_role") not in ["vendedor", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso solo para vendedores y administradores"
        )
    return current_user