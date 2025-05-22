from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class BusinessType(str, Enum):
    AGENCIA_VIAJES = "agencia_viajes"
    HOTEL = "hotel"
    RESTAURANTE = "restaurante"
    INDEPENDIENTE = "independiente"
    OTRO = "otro"

class DocumentType(str, Enum):
    CEDULA = "cedula"
    NIT = "nit"
    LICENCIA_FUNCIONAMIENTO = "licencia_funcionamiento"
    REFERENCIAS_COMERCIALES = "referencias_comerciales"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Schemas para crear solicitud
class VendorApplicationCreate(BaseModel):
    business_name: str = Field(..., min_length=3, max_length=255)
    business_type: BusinessType
    tax_id: Optional[str] = Field(None, max_length=50)
    business_address: Optional[str] = Field(None, max_length=500)
    business_phone: Optional[str] = Field(None, max_length=20)
    business_email: Optional[EmailStr] = None
    years_of_experience: Optional[int] = Field(0, ge=0, le=50)
    description: Optional[str] = Field(None, max_length=1000)
    why_want_to_sell: str = Field(..., min_length=50, max_length=2000)
    expected_sales_volume: Optional[int] = Field(None, ge=1)

    @validator('business_name')
    def validate_business_name(cls, v):
        return v.strip()

    @validator('why_want_to_sell')
    def validate_motivation(cls, v):
        if len(v.strip()) < 50:
            raise ValueError('Debe explicar con al menos 50 caracteres')
        return v.strip()

# Schema para documento
class DocumentUploadResponse(BaseModel):
    id: str
    document_type: DocumentType
    document_name: str
    file_url: str
    verification_status: VerificationStatus
    uploaded_at: datetime

# Schema para respuesta de aplicación
class VendorApplicationResponse(BaseModel):
    id: str
    business_name: str
    business_type: str
    application_status: ApplicationStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    documents: List[DocumentUploadResponse] = []

# Schema para admin
class VendorApplicationAdmin(BaseModel):
    id: str
    user_id: str
    applicant_name: str
    applicant_email: str
    business_name: str
    business_type: str
    tax_id: Optional[str]
    application_status: ApplicationStatus
    submitted_at: datetime
    documents_count: int
    why_want_to_sell: str

class ApplicationApprovalRequest(BaseModel):
    commission_rate: Optional[float] = Field(10.0, ge=0, le=50)
    notes: Optional[str] = None

class ApplicationRejectionRequest(BaseModel):
    rejection_reason: str = Field(..., min_length=10, max_length=500)