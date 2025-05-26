from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Header, Query
from typing import List, Optional
import uuid
import logging
from app.schemas.vendor import (
    VendorApplicationCreate, 
    VendorApplicationResponse,
    VendorApplicationAdmin,
    ApplicationApprovalRequest,
    ApplicationRejectionRequest
)
from app.services.vendor_service import VendorService
from app.dependencies import (
    get_current_client, 
    get_current_admin, 
    get_current_user
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vendor", tags=["vendor"])
vendor_service = VendorService()

# Endpoint para verificar que el router está funcionando
@router.get("/health")
async def vendor_health():
    """Health check para el módulo de vendor"""
    return {
        "message": "Vendor router is working",
        "status": "healthy"
    }

@router.post("/apply")
async def create_vendor_application(
    application: VendorApplicationCreate,
    current_user: dict = Depends(get_current_client)
):
    """Crear solicitud para ser vendedor (solo clientes)"""
    try:
        result = await vendor_service.create_application(
            uuid.UUID(current_user['id']), 
            application
        )
        return {
            "message": "Solicitud creada exitosamente",
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating application: {str(e)}"
        )

@router.post("/upload-document/{application_id}")
async def upload_document(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Subir documento para verificación"""
    try:
        result = await vendor_service.upload_document(
            uuid.UUID(application_id),
            document_type,
            file,
            uuid.UUID(current_user['id'])
        )
        return {
            "success": True,
            "message": "Documento subido exitosamente",
            **result
        }
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )

@router.get("/my-application", response_model=VendorApplicationResponse)
async def get_my_application(
    current_user: dict = Depends(get_current_user)
):
    """Obtener mi solicitud actual"""
    try:
        application = await vendor_service.get_user_application(
            uuid.UUID(current_user['id'])
        )
        
        if not application:
            raise HTTPException(
                status_code=404,
                detail="No tienes ninguna solicitud"
            )
        
        return application
    except Exception as e:
        logger.error(f"Error retrieving user application: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving application: {str(e)}"
        )

# ===== ENDPOINTS DE ADMINISTRADOR =====

@router.get("/admin/pending", response_model=List[VendorApplicationAdmin])
async def get_pending_applications(
    admin_user: dict = Depends(get_current_admin)
):
    """Obtener TODAS las solicitudes (no solo pendientes) - para admin"""
    try:
        logger.info("🔍 Admin requesting all applications")
        applications = await vendor_service.get_pending_applications()
        logger.info(f"✅ Retrieved {len(applications)} applications")
        return applications
    except Exception as e:
        logger.error(f"❌ Error retrieving applications: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving applications: {str(e)}"
        )

@router.get("/admin/application/{application_id}")
async def get_application_details(
    application_id: str,
    admin_user: dict = Depends(get_current_admin)
):
    """Obtener detalles completos de una solicitud (admin)"""
    logger.info(f"🔍 Admin requesting application details for: {application_id}")
    
    try:
        # Validar UUID
        try:
            app_uuid = uuid.UUID(application_id)
            logger.info(f"✅ Valid UUID: {app_uuid}")
        except ValueError as e:
            logger.error(f"❌ Invalid UUID format: {application_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid application ID format: {application_id}"
            )
        
        # Obtener aplicación
        logger.info("🔎 Calling vendor_service.get_application_by_id...")
        application = await vendor_service.get_application_by_id(app_uuid)
        
        if not application:
            logger.warning(f"❌ Application not found: {application_id}")
            raise HTTPException(
                status_code=404,
                detail="Solicitud no encontrada"
            )
        
        logger.info("✅ Application details retrieved successfully")
        return {
            "success": True,
            "data": application
        }
        
    except HTTPException as e:
        # Re-raise HTTP exceptions
        logger.error(f"❌ HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        # Log and convert other exceptions
        logger.error(f"❌ Unexpected error in get_application_details: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        logger.error(f"❌ Admin user: {admin_user.get('email', 'unknown')}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving application details: {str(e)}"
        )

@router.get("/admin/stats")
async def get_application_stats(
    admin_user: dict = Depends(get_current_admin)
):
    """Obtener estadísticas de solicitudes para dashboard"""
    try:
        logger.info("📊 Admin requesting application stats")
        stats = await vendor_service.get_application_stats()
        logger.info("✅ Stats retrieved successfully")
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )

@router.get("/admin/applications/by-status", response_model=List[VendorApplicationAdmin])
async def get_applications_by_status(
    status: str = Query(..., description="Estado de las solicitudes"),
    admin_user: dict = Depends(get_current_admin)
):
    """Obtener solicitudes por estado específico"""
    try:
        logger.info(f"🔍 Admin requesting applications with status: {status}")
        applications = await vendor_service.get_applications_by_status(status)
        logger.info(f"✅ Retrieved {len(applications)} applications with status {status}")
        return applications
    except Exception as e:
        logger.error(f"❌ Error retrieving applications by status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving applications by status: {str(e)}"
        )

@router.post("/admin/approve/{application_id}")
async def approve_application(
    application_id: str,
    approval_data: ApplicationApprovalRequest,
    admin_user: dict = Depends(get_current_admin)
):
    """Aprobar solicitud de vendedor"""
    try:
        logger.info(f"✅ Admin approving application: {application_id}")
        result = await vendor_service.approve_application(
            uuid.UUID(application_id),
            uuid.UUID(admin_user['id']),
            approval_data.commission_rate
        )
        logger.info("✅ Application approved successfully")
        return {
            "success": True,
            "message": "Solicitud aprobada exitosamente",
            **result
        }
    except Exception as e:
        logger.error(f"❌ Error approving application: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error approving application: {str(e)}"
        )

@router.post("/admin/reject/{application_id}")
async def reject_application(
    application_id: str,
    rejection_data: ApplicationRejectionRequest,
    admin_user: dict = Depends(get_current_admin)
):
    """Rechazar solicitud de vendedor"""
    try:
        logger.info(f"❌ Admin rejecting application: {application_id}")
        result = await vendor_service.reject_application(
            uuid.UUID(application_id),
            uuid.UUID(admin_user['id']),
            rejection_data.rejection_reason
        )
        logger.info("✅ Application rejected successfully")
        return {
            "success": True,
            "message": "Solicitud rechazada",
            **result
        }
    except Exception as e:
        logger.error(f"❌ Error rejecting application: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error rejecting application: {str(e)}"
        )

@router.put("/admin/update-status/{application_id}")
async def update_application_status(
    application_id: str,
    new_status: str = Query(..., description="Nuevo estado de la solicitud"),
    notes: Optional[str] = Query(None, description="Notas adicionales"),
    admin_user: dict = Depends(get_current_admin)
):
    """Actualizar estado de solicitud (genérico)"""
    try:
        logger.info(f"🔄 Admin updating status for {application_id} to {new_status}")
        result = await vendor_service.update_application_status(
            uuid.UUID(application_id),
            new_status,
            uuid.UUID(admin_user['id']),
            notes
        )
        logger.info("✅ Status updated successfully")
        return {
            "success": True,
            **result
        }
    except Exception as e:
        logger.error(f"❌ Error updating status: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error updating status: {str(e)}"
        )

# ===== ENDPOINTS PARA VENDEDORES =====

@router.get("/profile")
async def get_vendor_profile(
    current_user: dict = Depends(get_current_user)
):
    """Obtener perfil de vendedor (para vendedores aprobados)"""
    try:
        # Verificar que el usuario sea vendedor
        if current_user.get('role') != 'vendedor':
            raise HTTPException(
                status_code=403,
                detail="Solo los vendedores pueden acceder a este endpoint"
            )
        
        vendor = await vendor_service.get_vendor_by_user_id(
            uuid.UUID(current_user['id'])
        )
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Perfil de vendedor no encontrado"
            )
        
        return {
            "success": True,
            "data": vendor
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving vendor profile: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving vendor profile: {str(e)}"
        )

# ===== ENDPOINTS DE TESTING/DEBUG =====

@router.get("/test-connection")
async def test_vendor_connection():
    """Test endpoint para verificar la conexión con el servicio de vendor"""
    try:
        logger.info("🧪 Testing vendor service connection...")
        # Intentar obtener estadísticas básicas
        stats = await vendor_service.get_application_stats()
        logger.info("✅ Vendor service connection test passed")
        return {
            "success": True,
            "message": "Vendor service is accessible",
            "service_available": True,
            "sample_stats": {
                "total_applications": stats.get("total_applications", 0),
                "pending_count": stats.get("pending_count", 0)
            }
        }
    except Exception as e:
        logger.error(f"❌ Vendor service connection test failed: {e}")
        return {
            "success": False,
            "message": f"Vendor service error: {str(e)}",
            "service_available": False
        }

@router.get("/debug/all-applications")
async def debug_all_applications(
    admin_user: dict = Depends(get_current_admin)
):
    """Debug endpoint para ver todas las solicitudes con información completa"""
    try:
        logger.info("🐛 Debug: Admin requesting all applications with full info")
        applications = await vendor_service.get_pending_applications()
        logger.info(f"🐛 Debug: Retrieved {len(applications)} applications")
        
        return {
            "success": True,
            "count": len(applications),
            "applications": applications,
            "debug_info": {
                "service_name": "VendorService",
                "endpoint": "get_pending_applications",
                "admin_user": admin_user.get('email', 'unknown'),
                "timestamp": "2025-05-25 19:41:16"
            }
        }
    except Exception as e:
        logger.error(f"🐛 Debug endpoint failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "debug_info": {
                "service_name": "VendorService",
                "endpoint": "get_pending_applications - FAILED",
                "error_type": str(type(e))
            }
        }

@router.get("/debug/single-application/{application_id}")
async def debug_single_application(
    application_id: str,
    admin_user: dict = Depends(get_current_admin)
):
    """Debug endpoint para ver una aplicación específica paso a paso"""
    logger.info(f"🐛 DEBUG: Starting debug for application {application_id}")
    
    debug_steps = []
    
    try:
        # Step 1: Validate UUID
        debug_steps.append("Step 1: Validating UUID format")
        try:
            app_uuid = uuid.UUID(application_id)
            debug_steps.append(f"✅ Step 1 OK: Valid UUID {app_uuid}")
        except ValueError as e:
            debug_steps.append(f"❌ Step 1 FAILED: Invalid UUID {e}")
            return {"success": False, "debug_steps": debug_steps}
        
        # Step 2: Call service
        debug_steps.append("Step 2: Calling vendor service")
        try:
            application = await vendor_service.get_application_by_id(app_uuid)
            debug_steps.append("✅ Step 2 OK: Service call completed")
        except Exception as e:
            debug_steps.append(f"❌ Step 2 FAILED: Service error {e}")
            return {"success": False, "debug_steps": debug_steps, "error": str(e)}
        
        # Step 3: Check result
        debug_steps.append("Step 3: Checking result")
        if application:
            debug_steps.append(f"✅ Step 3 OK: Application found for business: {application.get('business_name', 'N/A')}")
            return {
                "success": True,
                "debug_steps": debug_steps,
                "application_summary": {
                    "id": application.get("id"),
                    "business_name": application.get("business_name"),
                    "status": application.get("application_status"),
                    "documents_count": len(application.get("documents", [])),
                    "history_count": len(application.get("history", []))
                }
            }
        else:
            debug_steps.append("❌ Step 3 FAILED: Application not found")
            return {"success": False, "debug_steps": debug_steps}
            
    except Exception as e:
        debug_steps.append(f"❌ UNEXPECTED ERROR: {e}")
        logger.error(f"🐛 DEBUG FAILED: {e}")
        return {
            "success": False,
            "debug_steps": debug_steps,
            "error": str(e),
            "error_type": str(type(e))
        }