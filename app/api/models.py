from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ========== REQUESTS ==========

class ContactCreate(BaseModel):
    email: EmailStr
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None


class NoteCreate(BaseModel):
    contact_identifier: str = Field(..., description="Email o ID del contacto")
    content: str = Field(default="", description="Contenido de la nota")


class ContactUpdate(BaseModel):
    contact_identifier: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    lifecyclestage: Optional[str] = None


# ========== RESPONSES ==========

class ContactResponse(BaseModel):
    id: str
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    hubspot_url: str
    message: str
    already_existed: bool = False


class NoteResponse(BaseModel):
    note_id: str
    contact_id: str
    contact_name: Optional[str] = None
    message: str
    hubspot_url: str


class ContactUpdateResponse(BaseModel):
    id: str
    contact_name: Optional[str] = None
    updated_fields: dict
    message: str
    hubspot_url: str


class HealthResponse(BaseModel):
    status: str
    version: str
    hubspot_connected: bool
    timestamp: datetime