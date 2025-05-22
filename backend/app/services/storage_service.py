# backend/app/services/storage_service.py
import os
import uuid
import httpx
import mimetypes
from fastapi import UploadFile, HTTPException
from typing import Optional, Tuple, List, Dict, Any
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    def __init__(self):
        self.base_url = os.getenv("SUPABASE_URL")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.bucket_name = "vendor-documents"
        self.max_size = int(os.getenv("MAX_UPLOAD_SIZE", "5242880"))  # 5MB default
        self.allowed_extensions = os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png").split(",")
        
        # Validar configuración crítica
        if not self.base_url or not self.service_key:
            logger.error("SUPABASE_URL or SUPABASE_SERVICE_KEY not configured")
            raise ValueError("Supabase storage not properly configured")
        
        logger.info(f"Storage service initialized. Bucket: {self.bucket_name}, Max size: {self.max_size} bytes")
    
    def _get_headers(self) -> Dict[str, str]:
        """Headers para autenticación con Supabase"""
        return {
            "Authorization": f"Bearer {self.service_key}",
            "apikey": self.service_key,
            "Content-Type": "application/json"
        }
    
    async def upload_document(
        self, 
        file: UploadFile, 
        user_id: str, 
        document_type: str
    ) -> Tuple[str, str]:
        """
        Sube un documento al storage de Supabase
        Returns: (file_url, file_path)
        """
        try:
            # Leer contenido del archivo
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Validar tamaño del archivo
            if len(file_content) > self.max_size:
                max_mb = self.max_size / 1024 / 1024
                raise HTTPException(
                    status_code=400,
                    detail=f"Archivo muy grande. Máximo {max_mb:.1f}MB permitido"
                )
            
            # Validar extensión del archivo
            file_extension = self._get_file_extension(file.filename)
            if not file_extension or file_extension not in self.allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de archivo no permitido. Solo se permiten: {', '.join(self.allowed_extensions)}"
                )
            
            # Validar que el archivo no esté vacío
            if len(file_content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="El archivo está vacío"
                )
            
            # Validar MIME type básico
            content_type = file.content_type or self._guess_content_type(file.filename)
            if not self._is_valid_mime_type(file_extension, content_type):
                logger.warning(f"MIME type mismatch: {content_type} for extension {file_extension}")
            
            # Generar nombre único para el archivo
            unique_filename = self._generate_unique_filename(user_id, document_type, file_extension)
            
            # URL para subir archivo a Supabase Storage
            upload_url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{unique_filename}"
            
            # Headers específicos para upload
            upload_headers = {
                "Authorization": f"Bearer {self.service_key}",
                "apikey": self.service_key,
                "Content-Type": content_type,
                "x-upsert": "false"  # No sobrescribir si existe
            }
            
            # Subir archivo usando httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    upload_url,
                    headers=upload_headers,
                    content=file_content
                )
                
                if response.status_code not in [200, 201]:
                    error_msg = f"Error uploading to Supabase: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise HTTPException(
                        status_code=500,
                        detail="Error al subir archivo al servidor de almacenamiento"
                    )
            
            # Generar URL pública del archivo
            public_url = f"{self.base_url}/storage/v1/object/public/{self.bucket_name}/{unique_filename}"
            
            logger.info(f"File uploaded successfully: {unique_filename} ({len(file_content)} bytes)")
            return public_url, unique_filename
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error interno al procesar archivo: {str(e)}"
            )
    
    async def delete_document(self, file_path: str) -> bool:
        """Elimina un documento del storage"""
        try:
            delete_url = f"{self.base_url}/storage/v1/object/{self.bucket_name}/{file_path}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    delete_url,
                    headers=self._get_headers()
                )
                
                success = response.status_code in [200, 204]
                if success:
                    logger.info(f"File deleted successfully: {file_path}")
                else:
                    logger.warning(f"Failed to delete file: {file_path} - Status: {response.status_code}")
                
                return success
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    async def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """Obtiene una URL firmada para acceso temporal al archivo"""
        try:
            signed_url_endpoint = f"{self.base_url}/storage/v1/object/sign/{self.bucket_name}/{file_path}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    signed_url_endpoint,
                    headers=self._get_headers(),
                    json={"expiresIn": expires_in}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    signed_url = f"{self.base_url}/storage/v1{data['signedURL']}"
                    logger.info(f"Signed URL generated for: {file_path} (expires in {expires_in}s)")
                    return signed_url
                
                logger.warning(f"Failed to generate signed URL for: {file_path} - Status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error generating signed URL for {file_path}: {str(e)}")
            return None
    
    async def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Lista todos los documentos de un usuario"""
        try:
            list_url = f"{self.base_url}/storage/v1/object/list/{self.bucket_name}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    list_url,
                    headers=self._get_headers(),
                    json={
                        "limit": 100,
                        "prefix": f"{user_id}/"
                    }
                )
                
                if response.status_code == 200:
                    documents = response.json()
                    logger.info(f"Listed {len(documents)} documents for user {user_id}")
                    return documents
                
                logger.warning(f"Failed to list documents for user {user_id} - Status: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing documents for user {user_id}: {str(e)}")
            return []
    
    async def check_bucket_exists(self) -> bool:
        """Verifica si el bucket existe"""
        try:
            list_url = f"{self.base_url}/storage/v1/bucket"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    list_url,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    buckets = response.json()
                    bucket_names = [bucket.get('name') for bucket in buckets]
                    exists = self.bucket_name in bucket_names
                    logger.info(f"Bucket '{self.bucket_name}' exists: {exists}")
                    return exists
                
                return False
        except Exception as e:
            logger.error(f"Error checking bucket existence: {str(e)}")
            return False
    
    def _get_file_extension(self, filename: str) -> str:
        """Obtiene la extensión del archivo en minúsculas"""
        if not filename or '.' not in filename:
            return ''
        return filename.split('.')[-1].lower().strip()
    
    def _guess_content_type(self, filename: str) -> str:
        """Adivina el content type basado en la extensión"""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
    
    def _is_valid_mime_type(self, extension: str, mime_type: str) -> bool:
        """Valida que el MIME type sea apropiado para la extensión"""
        allowed_mimes = {
            'pdf': ['application/pdf'],
            'jpg': ['image/jpeg'],
            'jpeg': ['image/jpeg'],
            'png': ['image/png']
        }
        
        expected_mimes = allowed_mimes.get(extension, [])
        return mime_type in expected_mimes if expected_mimes else True
    
    def _generate_unique_filename(self, user_id: str, document_type: str, extension: str) -> str:
        """Genera un nombre único para el archivo"""
        # Limpiar document_type para que sea seguro como nombre de archivo
        safe_doc_type = "".join(c for c in document_type if c.isalnum() or c in ('-', '_')).lower()
        unique_id = str(uuid.uuid4())
        timestamp = str(int(uuid.uuid1().time))
        
        return f"{user_id}/{safe_doc_type}_{timestamp}_{unique_id}.{extension}"