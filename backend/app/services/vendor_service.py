from typing import List, Optional, Dict, Any
import uuid
from uuid import UUID
from fastapi import HTTPException, UploadFile
from app.database import get_db
from app.schemas.vendor import (
    VendorApplicationCreate, 
    ApplicationStatus,
    VendorApplicationResponse,
    VendorApplicationAdmin
)
from app.services.storage_service import SupabaseStorageService
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class VendorService:
    def __init__(self):
        self.storage_service = SupabaseStorageService()
        self.email_service = EmailService()
    
    async def create_application(
        self, 
        user_id: UUID, 
        application_data: VendorApplicationCreate
    ) -> Dict[str, str]:
        """Crear nueva solicitud de vendedor"""
        async with get_db() as conn:
            # Verificar que no tenga solicitud pendiente
            existing = await conn.fetchrow(
                """
                SELECT id FROM vendor_applications 
                WHERE user_id = $1 AND application_status IN ('pending', 'under_review')
                """,
                user_id
            )
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Ya tienes una solicitud pendiente"
                )
            
            # Obtener datos del usuario
            user = await conn.fetchrow(
                "SELECT full_name, email FROM user_profiles WHERE id = $1",
                user_id
            )
            
            if not user:
                raise HTTPException(
                    status_code=404, 
                    detail="Usuario no encontrado"
                )
            
            # Crear solicitud
            application_id = await conn.fetchval(
                """
                INSERT INTO vendor_applications (
                    user_id, business_name, business_type, tax_id,
                    business_address, business_phone, business_email,
                    years_of_experience, description, why_want_to_sell,
                    expected_sales_volume, application_status
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
                """,
                user_id,
                application_data.business_name,
                application_data.business_type.value,
                application_data.tax_id,
                application_data.business_address,
                application_data.business_phone,
                application_data.business_email,
                application_data.years_of_experience,
                application_data.description,
                application_data.why_want_to_sell,
                application_data.expected_sales_volume,
                ApplicationStatus.PENDING.value
            )
            
            # Enviar emails
            try:
                await self.email_service.send_vendor_application_confirmation(
                    user['email'],
                    user['full_name'],
                    str(application_id)
                )
                
                await self._notify_admins(
                    application_id,
                    application_data.business_name,
                    user['full_name']
                )
            except Exception as e:
                logger.error(f"Error sending emails: {e}")
            
            return {"application_id": str(application_id)}
    
    async def upload_document(
        self,
        application_id: UUID,
        document_type: str,
        file: UploadFile,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Subir documento para verificación"""
        async with get_db() as conn:
            # Verificar permisos
            application = await conn.fetchrow(
                "SELECT user_id FROM vendor_applications WHERE id = $1",
                application_id
            )
            
            if not application or application['user_id'] != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="No tienes permisos para esta solicitud"
                )
            
            # Eliminar documento anterior si existe
            await self._delete_existing_document(conn, application_id, document_type)
            
            # Subir nuevo archivo
            file_url, file_path = await self.storage_service.upload_document(
                file, str(user_id), document_type
            )
            
            # Guardar en BD
            document_id = await conn.fetchval(
                """
                INSERT INTO verification_documents (
                    application_id, document_type, document_name,
                    file_url, file_size, mime_type
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
                """,
                application_id, document_type, file.filename,
                file_url, file.size, file.content_type
            )
            
            return {
                "document_id": str(document_id),
                "file_url": file_url,
                "message": "Documento subido exitosamente"
            }
    
    async def get_user_application(self, user_id: UUID) -> Optional[VendorApplicationResponse]:
        """Obtener solicitud del usuario"""
        async with get_db() as conn:
            # Obtener solicitud
            application = await conn.fetchrow(
                """
                SELECT * FROM vendor_applications 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT 1
                """,
                user_id
            )
            
            if not application:
                return None
            
            # Obtener documentos
            documents = await conn.fetch(
                """
                SELECT id, document_type, document_name, file_url,
                       verification_status, uploaded_at
                FROM verification_documents
                WHERE application_id = $1
                ORDER BY uploaded_at DESC
                """,
                application['id']
            )
            
            # Construir respuesta
            return VendorApplicationResponse(
                id=str(application['id']),
                business_name=application['business_name'],
                business_type=application['business_type'],
                application_status=application['application_status'],
                submitted_at=application['submitted_at'],
                reviewed_at=application.get('reviewed_at'),
                rejection_reason=application.get('rejection_reason'),
                documents=[
                    {
                        "id": str(doc['id']),
                        "document_type": doc['document_type'],
                        "document_name": doc['document_name'],
                        "file_url": doc['file_url'],
                        "verification_status": doc['verification_status'],
                        "uploaded_at": doc['uploaded_at']
                    }
                    for doc in documents
                ]
            )
    
    async def get_pending_applications(self) -> List[VendorApplicationAdmin]:
        """Obtener solicitudes pendientes (admin)"""
        async with get_db() as conn:
            applications = await conn.fetch(
                """
                SELECT va.*, up.full_name as applicant_name, up.email as applicant_email,
                       COUNT(vd.id) as documents_count
                FROM vendor_applications va
                JOIN user_profiles up ON va.user_id = up.id
                LEFT JOIN verification_documents vd ON va.id = vd.application_id
                WHERE va.application_status = 'pending'
                GROUP BY va.id, up.full_name, up.email
                ORDER BY va.submitted_at ASC
                """
            )
            
            return [
                VendorApplicationAdmin(
                    id=str(app['id']),
                    user_id=str(app['user_id']),
                    applicant_name=app['applicant_name'],
                    applicant_email=app['applicant_email'],
                    business_name=app['business_name'],
                    business_type=app['business_type'],
                    tax_id=app.get('tax_id'),
                    application_status=app['application_status'],
                    submitted_at=app['submitted_at'],
                    documents_count=app['documents_count'],
                    why_want_to_sell=app['why_want_to_sell']
                )
                for app in applications
            ]
    
    async def approve_application(
        self,
        application_id: UUID,
        admin_id: UUID,
        commission_rate: float = 10.0
    ) -> Dict[str, str]:
        """Aprobar solicitud de vendedor"""
        async with get_db() as conn:
            async with conn.transaction():
                # Obtener datos de la solicitud
                application = await conn.fetchrow(
                    """
                    SELECT va.user_id, va.business_name, up.full_name, up.email
                    FROM vendor_applications va
                    JOIN user_profiles up ON va.user_id = up.id
                    WHERE va.id = $1 AND va.application_status = 'pending'
                    """,
                    application_id
                )
                
                if not application:
                    raise HTTPException(
                        status_code=404,
                        detail="Solicitud no encontrada o ya procesada"
                    )
                
                # Actualizar solicitud
                await conn.execute(
                    """
                    UPDATE vendor_applications 
                    SET application_status = 'approved', 
                        reviewed_by = $1, 
                        reviewed_at = NOW(),
                        approved_at = NOW()
                    WHERE id = $2
                    """,
                    admin_id, application_id
                )
                
                # Promover usuario a vendedor
                await conn.execute(
                    """
                    UPDATE user_profiles 
                    SET user_role = 'vendedor', 
                        is_verified = true,
                        verification_status = 'approved',
                        updated_at = NOW()
                    WHERE id = $1
                    """,
                    application['user_id']
                )
                
                # Crear configuración de vendedor
                await conn.execute(
                    """
                    INSERT INTO vendor_settings (
                        user_id, commission_rate, activated_at
                    ) VALUES ($1, $2, NOW())
                    """,
                    application['user_id'], commission_rate
                )
                
                # Registrar cambio de rol
                await conn.execute(
                    """
                    INSERT INTO role_change_history (
                        user_id, previous_role, new_role, changed_by, reason
                    ) VALUES ($1, 'cliente', 'vendedor', $2, 'Promoción tras verificación')
                    """,
                    application['user_id'], admin_id
                )
                
                # Enviar email de aprobación
                try:
                    await self.email_service.send_vendor_approval(
                        application['email'],
                        application['full_name'],
                        application['business_name']
                    )
                except Exception as e:
                    logger.error(f"Error sending approval email: {e}")
                
                return {"message": "Solicitud aprobada exitosamente"}
    
    async def reject_application(
        self,
        application_id: UUID,
        admin_id: UUID,
        rejection_reason: str
    ) -> Dict[str, str]:
        """Rechazar solicitud de vendedor"""
        async with get_db() as conn:
            # Obtener datos de la solicitud
            application = await conn.fetchrow(
                """
                SELECT va.user_id, up.full_name, up.email
                FROM vendor_applications va
                JOIN user_profiles up ON va.user_id = up.id
                WHERE va.id = $1 AND va.application_status = 'pending'
                """,
                application_id
            )
            
            if not application:
                raise HTTPException(
                    status_code=404,
                    detail="Solicitud no encontrada o ya procesada"
                )
            
            # Actualizar solicitud
            await conn.execute(
                """
                UPDATE vendor_applications 
                SET application_status = 'rejected',
                    reviewed_by = $1,
                    reviewed_at = NOW(),
                    rejection_reason = $2
                WHERE id = $3
                """,
                admin_id, rejection_reason, application_id
            )
            
            # Enviar email de rechazo
            try:
                await self.email_service.send_vendor_rejection(
                    application['email'],
                    application['full_name'],
                    rejection_reason
                )
            except Exception as e:
                logger.error(f"Error sending rejection email: {e}")
            
            return {"message": "Solicitud rechazada"}
    
    async def _delete_existing_document(self, conn, application_id: UUID, document_type: str):
        """Eliminar documento existente"""
        existing_doc = await conn.fetchrow(
            """
            SELECT id, file_url FROM verification_documents 
            WHERE application_id = $1 AND document_type = $2
            """,
            application_id, document_type
        )
        
        if existing_doc:
            # Extraer path del archivo
            file_url = existing_doc['file_url']
            if 'vendor-documents/' in file_url:
                file_path = file_url.split('vendor-documents/')[-1]
                await self.storage_service.delete_document(file_path)
            
            # Eliminar de BD
            await conn.execute(
                "DELETE FROM verification_documents WHERE id = $1",
                existing_doc['id']
            )
    
    async def _notify_admins(self, application_id: UUID, business_name: str, applicant_name: str):
        """Notificar a administradores"""
        async with get_db() as conn:
            admins = await conn.fetch(
                "SELECT email FROM user_profiles WHERE user_role = 'administrador' AND is_active = true"
            )
            
            for admin in admins:
                try:
                    await self.email_service.send_admin_notification(
                        admin['email'],
                        str(application_id),
                        business_name,
                        applicant_name
                    )
                except Exception as e:
                    logger.error(f"Error notifying admin {admin['email']}: {e}")