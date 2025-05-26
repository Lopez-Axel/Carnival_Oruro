# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno ANTES de cualquier import
print("Loading environment variables...")
env_loaded = load_dotenv()
print(f"Environment loaded: {env_loaded}")

# Debug: verificar DATABASE_URL
database_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL loaded: {'Yes' if database_url else 'No'}")
if database_url:
    print(f"DATABASE_URL preview: {database_url[:30]}...{database_url[-10:]}")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Carnaval Oruro API",
    description="API para venta de entradas del Carnaval de Oruro",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# IMPORTAR Y REGISTRAR ROUTERS
# ===============================

# Importar routers
from app.routes.vendor import router as vendor_router

# Registrar routers con prefijo /api
app.include_router(vendor_router, prefix="/api")

# ===============================
# IMPORTAR Y REGISTRAR ROUTERS
# ===============================

# Importar routers
from app.routes.vendor import router as vendor_router

# Registrar routers con prefijo /api
app.include_router(vendor_router, prefix="/api")

# Endpoint de debug para ver rutas
@app.get("/debug-routes")
async def debug_routes():
    """Debug endpoint para ver todas las rutas disponibles"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed')
            })
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path'])
    }

@app.on_event("startup")
async def startup_event():
    """Eventos de inicio"""
    logger.info("Starting up...")
    
    # Debug de variables de entorno al startup
    database_url = os.getenv("DATABASE_URL")
    logger.info(f"DATABASE_URL at startup: {'Found' if database_url else 'NOT FOUND'}")
    
    try:
        from app.database import Database
        await Database.create_pool()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de cierre"""
    logger.info("Shutting down...")
    try:
        from app.database import Database
        await Database.close_pool()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

@app.get("/")
async def root():
    return {
        "message": "Carnaval Oruro API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/debug-env")
async def debug_env():
    """Debug endpoint para verificar variables de entorno"""
    database_url = os.getenv("DATABASE_URL")
    supabase_url = os.getenv("SUPABASE_URL")
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    
    return {
        "working_directory": os.getcwd(),
        "env_file_exists": os.path.exists(".env"),
        "database_url_loaded": bool(database_url),
        "database_url_preview": database_url[:30] + "..." if database_url else None,
        "supabase_url": supabase_url,
        "sendgrid_configured": bool(sendgrid_key),
        "environment_vars_count": len([k for k in os.environ.keys() if k.startswith(('DATABASE', 'SUPABASE', 'SENDGRID'))])
    }

# Endpoint para listar todas las rutas disponibles
@app.get("/debug-routes")
async def debug_routes():
    """Debug endpoint para ver todas las rutas disponibles"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed')
            })
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path'])
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": "DATABASE_URL not found in environment variables",
                "debug": {
                    "working_dir": os.getcwd(),
                    "env_file_exists": os.path.exists(".env"),
                    "env_vars_with_db": [k for k in os.environ.keys() if 'DATABASE' in k]
                }
            }
        
        from app.database import get_db
        
        async with get_db() as conn:
            result = await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected" if result == 1 else "error"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Endpoint para listar todas las rutas disponibles
@app.get("/debug-routes")
async def debug_routes():
    """Debug endpoint para ver todas las rutas disponibles"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unnamed')
            })
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path'])
    }

# ===============================
# ENDPOINTS DE PRUEBA - STORAGE
# ===============================

@app.get("/test-storage-config")
async def test_storage_config():
    """Verifica la configuración del servicio de storage"""
    try:
        from app.services.storage_service import SupabaseStorageService
        
        storage = SupabaseStorageService()
        
        # Verificar si el bucket existe
        bucket_exists = await storage.check_bucket_exists()
        
        return {
            "success": True,
            "storage_configured": True,
            "bucket_name": storage.bucket_name,
            "bucket_exists": bucket_exists,
            "max_upload_size_mb": storage.max_size / 1024 / 1024,
            "allowed_extensions": storage.allowed_extensions,
            "supabase_url": storage.base_url,
            "service_key_configured": bool(storage.service_key)
        }
    except Exception as e:
        logger.error(f"Storage config test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "storage_configured": False
        }

@app.post("/test-storage-upload")
async def test_storage_upload(
    file: UploadFile = File(...),
    user_id: str = Form(default="test-user"),
    document_type: str = Form(default="test-document")
):
    """Test endpoint para probar subida de archivos"""
    try:
        from app.services.storage_service import SupabaseStorageService
        
        logger.info(f"Testing storage upload: {file.filename} ({file.size} bytes)")
        
        storage = SupabaseStorageService()
        
        # Subir archivo
        file_url, file_path = await storage.upload_document(file, user_id, document_type)
        
        return {
            "success": True,
            "message": "Archivo subido exitosamente",
            "file_info": {
                "original_name": file.filename,
                "content_type": file.content_type,
                "size_bytes": file.size,
                "file_url": file_url,
                "file_path": file_path
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Storage upload test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-storage-list/{user_id}")
async def test_storage_list(user_id: str):
    """Lista archivos de un usuario específico"""
    try:
        from app.services.storage_service import SupabaseStorageService
        
        storage = SupabaseStorageService()
        documents = await storage.list_user_documents(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "documents_count": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"Storage list test failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ===============================
# ENDPOINTS DE PRUEBA - EMAIL
# ===============================

@app.get("/test-email-config")
async def test_email_config():
    """Verifica la configuración del servicio de email"""
    try:
        from app.services.email_service import EmailService
        
        email_service = EmailService()
        
        return {
            "success": True,
            "email_configured": bool(email_service.sg),
            "from_email": email_service.from_email,
            "base_url": email_service.base_url,
            "sendgrid_configured": bool(email_service.sendgrid_api_key)
        }
    except Exception as e:
        logger.error(f"Email config test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "email_configured": False
        }

@app.post("/test-email-confirmation")
async def test_email_confirmation(
    email: str = Form(...),
    name: str = Form(default="Usuario de Prueba"),
    application_id: str = Form(default="TEST-12345")
):
    """Test endpoint para email de confirmación de solicitud"""
    try:
        from app.services.email_service import EmailService
        
        logger.info(f"Testing confirmation email to: {email}")
        
        email_service = EmailService()
        
        await email_service.send_vendor_application_confirmation(
            email, 
            name, 
            application_id
        )
        
        return {
            "success": True,
            "message": f"Email de confirmación enviado exitosamente a {email}",
            "email_type": "vendor_application_confirmation",
            "recipient": email
        }
    except Exception as e:
        logger.error(f"Email confirmation test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-email-admin-notification")
async def test_email_admin_notification(
    admin_email: str = Form(...),
    application_id: str = Form(default="TEST-12345"),
    business_name: str = Form(default="Empresa de Prueba"),
    applicant_name: str = Form(default="Usuario de Prueba")
):
    """Test endpoint para email de notificación a admin"""
    try:
        from app.services.email_service import EmailService
        
        logger.info(f"Testing admin notification email to: {admin_email}")
        
        email_service = EmailService()
        
        await email_service.send_admin_notification(
            admin_email,
            application_id,
            business_name,
            applicant_name
        )
        
        return {
            "success": True,
            "message": f"Email de notificación enviado exitosamente a {admin_email}",
            "email_type": "admin_notification",
            "recipient": admin_email
        }
    except Exception as e:
        logger.error(f"Email admin notification test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-email-approval")
async def test_email_approval(
    email: str = Form(...),
    name: str = Form(default="Usuario de Prueba"),
    business_name: str = Form(default="Empresa de Prueba")
):
    """Test endpoint para email de aprobación"""
    try:
        from app.services.email_service import EmailService
        
        logger.info(f"Testing approval email to: {email}")
        
        email_service = EmailService()
        
        await email_service.send_vendor_approval(
            email,
            name,
            business_name
        )
        
        return {
            "success": True,
            "message": f"Email de aprobación enviado exitosamente a {email}",
            "email_type": "vendor_approval",
            "recipient": email
        }
    except Exception as e:
        logger.error(f"Email approval test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-email-rejection")
async def test_email_rejection(
    email: str = Form(...),
    name: str = Form(default="Usuario de Prueba"),
    rejection_reason: str = Form(default="Los documentos proporcionados no cumplen con los requisitos mínimos.")
):
    """Test endpoint para email de rechazo"""
    try:
        from app.services.email_service import EmailService
        
        logger.info(f"Testing rejection email to: {email}")
        
        email_service = EmailService()
        
        await email_service.send_vendor_rejection(
            email,
            name,
            rejection_reason
        )
        
        return {
            "success": True,
            "message": f"Email de rechazo enviado exitosamente a {email}",
            "email_type": "vendor_rejection",
            "recipient": email
        }
    except Exception as e:
        logger.error(f"Email rejection test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# ENDPOINT COMBINADO DE PRUEBA
# ===============================

@app.get("/test-all-services")
async def test_all_services():
    """Prueba todos los servicios de una vez"""
    results = {
        "database": {"status": "unknown"},
        "storage": {"status": "unknown"},
        "email": {"status": "unknown"}
    }
    
    # Test Database
    try:
        from app.database import get_db
        async with get_db() as conn:
            await conn.fetchval("SELECT 1")
        results["database"] = {"status": "ok", "message": "Database connected"}
    except Exception as e:
        results["database"] = {"status": "error", "message": str(e)}
    
    # Test Storage
    try:
        from app.services.storage_service import SupabaseStorageService
        storage = SupabaseStorageService()
        bucket_exists = await storage.check_bucket_exists()
        results["storage"] = {
            "status": "ok", 
            "message": "Storage service configured",
            "bucket_exists": bucket_exists
        }
    except Exception as e:
        results["storage"] = {"status": "error", "message": str(e)}
    
    # Test Email
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        results["email"] = {
            "status": "ok" if email_service.sg else "warning",
            "message": "Email service configured" if email_service.sg else "Email service available but SendGrid not configured"
        }
    except Exception as e:
        results["email"] = {"status": "error", "message": str(e)}
    
    # Overall status
    all_ok = all(r["status"] == "ok" for r in results.values())
    
    return {
        "overall_status": "healthy" if all_ok else "partial",
        "services": results,
        "timestamp": "2025-05-22T12:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)