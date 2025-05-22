# app/database.py
import asyncpg
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def create_pool(cls):
        """Crear pool de conexiones a la base de datos"""
        if cls._pool is None:
            try:
                database_url = os.getenv("DATABASE_URL")
                
                if not database_url:
                    raise ValueError("DATABASE_URL not found in environment variables")
                
                cls._pool = await asyncpg.create_pool(
                    database_url,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                
                logger.info("Database pool created successfully")
                
            except Exception as e:
                logger.error(f"Error creating database pool: {e}")
                raise
                
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        """Cerrar pool de conexiones"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database pool closed")

@asynccontextmanager
async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """Context manager para obtener conexión a la base de datos"""
    pool = await Database.create_pool()
    async with pool.acquire() as connection:
        try:
            yield connection
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise