from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    
class UserCreate(UserBase):
    google_id: str
    photo_url: str | None = None

class User(UserBase):
    id: str
    google_id: str
    photo_url: str | None = None
    created_at: str
    
    class Config:
        from_attributes = True