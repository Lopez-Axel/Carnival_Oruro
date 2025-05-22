from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List
import uuid
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

router = APIRouter(prefix="/vendor", tags=["vendor"])
vendor_service = VendorService()

@router.post("/apply")
async def create_vendor_application(
    application: VendorApplicationCreate,
    current_user: dict = Depends(get_current_client)
):
    """Crear solicitud para ser vendedor (solo clientes)"""
    result = await vendor_service.create_application(
        uuid.UUID(current_user['id']), 
        application
    )
    return {
        "message": "Solicitud creada exitosamente",
        **result
    }

@router.post("/upload-document/{application_id}")
async def upload_document(
    application_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Subir documento para verificación"""
    result = await vendor_service.upload_document(
        uuid.UUID(application_id),
        document_type,
        file,
        uuid.UUID(current_user['id'])
    )
    return result

@router.get("/my-application", response_model=VendorApplicationResponse)
async def get_my_application(
    current_user: dict = Depends(get_current_user)
):
    """Obtener mi solicitud actual"""
    application = await vendor_service.get_user_application(
        uuid.UUID(current_user['id'])
    )
    
    if not application:
        raise HTTPException(
            status_code=404,
            detail="No tienes ninguna solicitud"
        )
    
    return application

# Endpoints de administrador
@router.get("/admin/pending", response_model=List[VendorApplicationAdmin])
async def get_pending_applications(
    admin_user: dict = Depends(get_current_admin)
):
    """Obtener solicitudes pendientes (solo admin)"""
    applications = await vendor_service.get_pending_applications()
    return applications

@router.post("/admin/approve/{application_id}")
async def approve_application(
    application_id: str,
    approval_data: ApplicationApprovalRequest,
    admin_user: dict = Depends(get_current_admin)
):
    """Aprobar solicitud de vendedor"""
    result = await vendor_service.approve_application(
        uuid.UUID(application_id),
        uuid.UUID(admin_user['id']),
        approval_data.commission_rate
    )
    return result

@router.post("/admin/reject/{application_id}")
async def reject_application(
    application_id: str,
    rejection_data: ApplicationRejectionRequest,
    admin_user: dict = Depends(get_current_admin)
):
    """Rechazar solicitud de vendedor"""
    result = await vendor_service.reject_application(
        uuid.UUID(application_id),
        uuid.UUID(admin_user['id']),
        rejection_data.rejection_reason
    )
    return result

@router.get("/admin/application/{application_id}")
async def get_application_details(
    application_id: str,
    admin_user: dict = Depends(get_current_admin)
):
    """Obtener detalles completos de una solicitud (admin)"""
    # Implementar según necesidades
    pass