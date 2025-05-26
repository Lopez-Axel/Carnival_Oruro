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
        """Obtener TODAS las solicitudes (no solo pendientes) para el admin"""
        async with get_db() as conn:
            applications = await conn.fetch(
                """
                SELECT va.*, up.full_name as applicant_name, up.email as applicant_email,
                       COUNT(vd.id) as documents_count
                FROM vendor_applications va
                JOIN user_profiles up ON va.user_id = up.id
                LEFT JOIN verification_documents vd ON va.id = vd.application_id
                GROUP BY va.id, up.full_name, up.email
                ORDER BY va.submitted_at DESC
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

    async def get_application_by_id(self, application_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtener detalles completos de una solicitud por ID (admin) - CON DEBUG"""
        logger.info(f"🔍 Getting application details for ID: {application_id}")
        
        try:
            async with get_db() as conn:
                logger.info("📡 Database connection established")
                
                # Obtener solicitud con datos del usuario
                logger.info("🔎 Fetching application with user data...")
                application = await conn.fetchrow(
                    """
                    SELECT va.*, up.full_name as applicant_name, up.email as applicant_email,
                           up.phone as applicant_phone, up.created_at as user_created_at
                    FROM vendor_applications va
                    JOIN user_profiles up ON va.user_id = up.id
                    WHERE va.id = $1
                    """,
                    application_id
                )
                
                if not application:
                    logger.warning(f"❌ Application not found for ID: {application_id}")
                    return None
                
                logger.info(f"✅ Application found: {application['business_name']}")
                
                # Obtener documentos
                logger.info("📄 Fetching documents...")
                documents = await conn.fetch(
                    """
                    SELECT id, document_type, document_name, file_url,
                           file_size, mime_type, verification_status, 
                           uploaded_at, verified_at
                    FROM verification_documents
                    WHERE application_id = $1
                    ORDER BY uploaded_at DESC
                    """,
                    application_id
                )
                
                logger.info(f"📄 Found {len(documents)} documents")
                
                # Obtener historial de cambios si existe (simplificado por ahora)
                logger.info("📋 Fetching role change history...")
                try:
                    # Primero intentamos ver qué columnas existen
                    test_history = await conn.fetchrow(
                        """
                        SELECT * FROM role_change_history 
                        WHERE user_id = $1 
                        LIMIT 1
                        """,
                        application['user_id']
                    )
                    
                    if test_history:
                        logger.info(f"📋 History table columns: {list(test_history.keys())}")
                        
                        # Ahora obtenemos todos los registros
                        history = await conn.fetch(
                            """
                            SELECT rch.*, up.full_name as changed_by_name
                            FROM role_change_history rch
                            LEFT JOIN user_profiles up ON rch.changed_by = up.id
                            WHERE rch.user_id = $1
                            ORDER BY rch.created_at DESC
                            """,
                            application['user_id']
                        )
                    else:
                        history = []
                    
                    logger.info(f"📋 Found {len(history)} history records")
                except Exception as e:
                    logger.error(f"❌ Error fetching history (continuing anyway): {e}")
                    history = []
                
                # Construir respuesta paso a paso
                logger.info("🏗️ Building response object...")
                
                try:
                    response_data = {
                        "id": str(application['id']),
                        "user_id": str(application['user_id']),
                        "applicant_name": application.get('applicant_name', 'N/A'),
                        "applicant_email": application.get('applicant_email', 'N/A'),
                        "applicant_phone": application.get('applicant_phone'),
                        "user_created_at": application.get('user_created_at'),
                        "business_name": application.get('business_name', 'N/A'),
                        "business_type": application.get('business_type', 'N/A'),
                        "tax_id": application.get('tax_id'),
                        "business_address": application.get('business_address'),
                        "business_phone": application.get('business_phone'),
                        "business_email": application.get('business_email'),
                        "years_of_experience": application.get('years_of_experience'),
                        "description": application.get('description'),
                        "why_want_to_sell": application.get('why_want_to_sell'),
                        "expected_sales_volume": application.get('expected_sales_volume'),
                        "application_status": application.get('application_status', 'unknown'),
                        "submitted_at": application.get('submitted_at'),
                        "reviewed_at": application.get('reviewed_at'),
                        "approved_at": application.get('approved_at'),
                        "reviewed_by": str(application['reviewed_by']) if application.get('reviewed_by') else None,
                        "rejection_reason": application.get('rejection_reason'),
                    }
                    
                    logger.info("📄 Processing documents...")
                    response_data["documents"] = []
                    for doc in documents:
                        try:
                            doc_data = {
                                "id": str(doc['id']),
                                "document_type": doc.get('document_type', 'unknown'),
                                "document_name": doc.get('document_name', 'unknown'),
                                "file_url": doc.get('file_url', ''),
                                "file_size": doc.get('file_size', 0),
                                "mime_type": doc.get('mime_type', ''),
                                "verification_status": doc.get('verification_status', 'pending'),
                                "uploaded_at": doc.get('uploaded_at'),
                                "verified_at": doc.get('verified_at')
                            }
                            response_data["documents"].append(doc_data)
                        except Exception as e:
                            logger.error(f"❌ Error processing document {doc.get('id', 'unknown')}: {e}")
                    
                    logger.info("📋 Processing history...")
                    response_data["history"] = []
                    for h in history:
                        try:
                            # Usar las columnas que realmente existen
                            history_data = {
                                "id": str(h.get('id', 'unknown')),
                                "previous_role": h.get('previous_role', 'unknown'),
                                "new_role": h.get('new_role', 'unknown'),
                                "reason": h.get('reason', ''),
                                "changed_by_name": h.get('changed_by_name', 'System')
                            }
                            
                            # Intentar diferentes nombres de columna para la fecha
                            if 'created_at' in h:
                                history_data["created_at"] = h['created_at']
                            elif 'changed_at' in h:
                                history_data["created_at"] = h['changed_at']
                            elif 'timestamp' in h:
                                history_data["created_at"] = h['timestamp']
                            else:
                                history_data["created_at"] = None
                            
                            response_data["history"].append(history_data)
                        except Exception as e:
                            logger.error(f"❌ Error processing history record {h.get('id', 'unknown')}: {e}")
                    
                    logger.info("✅ Response object built successfully")
                    return response_data
                    
                except Exception as e:
                    logger.error(f"❌ Error building response object: {e}")
                    logger.error(f"Application data keys: {list(application.keys()) if application else 'None'}")
                    raise e
                    
        except Exception as e:
            logger.error(f"❌ Error in get_application_by_id: {e}")
            logger.error(f"Error type: {type(e)}")
            raise e

    async def get_applications_by_status(self, status: str) -> List[VendorApplicationAdmin]:
        """Obtener solicitudes por estado específico"""
        async with get_db() as conn:
            applications = await conn.fetch(
                """
                SELECT va.*, up.full_name as applicant_name, up.email as applicant_email,
                       COUNT(vd.id) as documents_count
                FROM vendor_applications va
                JOIN user_profiles up ON va.user_id = up.id
                LEFT JOIN verification_documents vd ON va.id = vd.application_id
                WHERE va.application_status = $1
                GROUP BY va.id, up.full_name, up.email
                ORDER BY va.submitted_at DESC
                """,
                status
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

    async def get_application_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de solicitudes para dashboard"""
        async with get_db() as conn:
            # Estadísticas básicas
            stats = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_applications,
                    COUNT(*) FILTER (WHERE application_status = 'pending') as pending_count,
                    COUNT(*) FILTER (WHERE application_status = 'approved') as approved_count,
                    COUNT(*) FILTER (WHERE application_status = 'rejected') as rejected_count,
                    COUNT(*) FILTER (WHERE application_status = 'under_review') as under_review_count
                FROM vendor_applications
                """
            )
            
            # Aplicaciones recientes (últimos 7 días)
            recent_count = await conn.fetchval(
                """
                SELECT COUNT(*) FROM vendor_applications 
                WHERE submitted_at >= NOW() - INTERVAL '7 days'
                """
            )
            
            # Aplicaciones por tipo de negocio
            business_types = await conn.fetch(
                """
                SELECT business_type, COUNT(*) as count
                FROM vendor_applications
                GROUP BY business_type
                ORDER BY count DESC
                """
            )
            
            return {
                "total_applications": stats['total_applications'],
                "pending_count": stats['pending_count'],
                "approved_count": stats['approved_count'],
                "rejected_count": stats['rejected_count'],
                "under_review_count": stats['under_review_count'],
                "recent_applications": recent_count,
                "business_types": [
                    {"type": bt['business_type'], "count": bt['count']}
                    for bt in business_types
                ],
                "approval_rate": round(
                    (stats['approved_count'] / max(stats['total_applications'], 1)) * 100, 2
                ) if stats['total_applications'] > 0 else 0
            }

    async def update_application_status(
        self, 
        application_id: UUID, 
        new_status: str, 
        admin_id: UUID,
        notes: Optional[str] = None
    ) -> Dict[str, str]:
        """Actualizar estado de solicitud (genérico)"""
        async with get_db() as conn:
            # Verificar que la solicitud existe
            application = await conn.fetchrow(
                "SELECT id, application_status FROM vendor_applications WHERE id = $1",
                application_id
            )
            
            if not application:
                raise HTTPException(
                    status_code=404,
                    detail="Solicitud no encontrada"
                )
            
            # Actualizar estado
            await conn.execute(
                """
                UPDATE vendor_applications 
                SET application_status = $1,
                    reviewed_by = $2,
                    reviewed_at = NOW(),
                    notes = COALESCE($3, notes)
                WHERE id = $4
                """,
                new_status, admin_id, notes, application_id
            )
            
            return {"message": f"Estado actualizado a {new_status}"}

    async def get_vendor_by_user_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtener información de vendedor por user_id"""
        async with get_db() as conn:
            vendor = await conn.fetchrow(
                """
                SELECT up.*, vs.commission_rate, vs.activated_at, vs.is_active as vendor_active,
                       vs.total_sales, vs.total_commission
                FROM user_profiles up
                LEFT JOIN vendor_settings vs ON up.id = vs.user_id
                WHERE up.id = $1 AND up.role = 'vendedor'
                """,
                user_id
            )
            
            if not vendor:
                return None
                
            return {
                "id": str(vendor['id']),
                "full_name": vendor['full_name'],
                "email": vendor['email'],
                "phone": vendor.get('phone'),
                "user_role": vendor['role'],
                "is_verified": vendor['is_verified'],
                "commission_rate": vendor.get('commission_rate'),
                "activated_at": vendor.get('activated_at'),
                "vendor_active": vendor.get('vendor_active', False),
                "total_sales": vendor.get('total_sales', 0),
                "total_commission": vendor.get('total_commission', 0)
            }

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
                    SET role = 'vendedor', 
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
                        user_id, commission_rate, activated_at, is_active
                    ) VALUES ($1, $2, NOW(), true)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        commission_rate = $2,
                        activated_at = NOW(),
                        is_active = true
                    """,
                    application['user_id'], commission_rate
                )
                
                # Registrar cambio de rol
                await conn.execute(
                    """
                    INSERT INTO role_change_history (
                        user_id, previous_role, new_role, changed_by, reason, created_at
                    ) VALUES ($1, 'cliente', 'vendedor', $2, 'Promoción tras verificación', NOW())
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
                "SELECT email FROM user_profiles WHERE role = 'administrador' AND is_active = true"
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