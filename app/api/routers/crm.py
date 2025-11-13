from fastapi import APIRouter, HTTPException, status
from app.api.models import (
    ContactCreate, ContactResponse,
    NoteCreate, NoteResponse,
    ContactUpdate, ContactUpdateResponse
)
from app.api.services.crm_service import CRMService
import logging

router = APIRouter(prefix="/crm", tags=["CRM"])
logger = logging.getLogger(__name__)
crm_service = CRMService()


@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate):
    """CASO 1: Crear un contacto con idempotencia"""
    try:
        result = await crm_service.create_contact_with_idempotency(contact)
        
        contact_data = result["contact"]
        props = contact_data.get("properties", {})
        
        return ContactResponse(
            id=contact_data["id"],
            email=props.get("email", contact.email),
            firstname=props.get("firstname"),
            lastname=props.get("lastname"),
            phone=props.get("phone"),
            hubspot_url=crm_service.hubspot.get_contact_url(contact_data["id"]),
            message=result["message"],
            already_existed=result["already_existed"]
        )
        
    except Exception as e:
        logger.error(f"Error al crear contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/contact/note", response_model=NoteResponse)
async def add_note_to_contact(note: NoteCreate):
    """CASO 2: Agregar una nota a un contacto"""
    try:
        result = await crm_service.add_note_to_contact(note)
        
        return NoteResponse(
            note_id=result["note_id"],
            contact_id=result["contact_id"],
            contact_name=result["contact_name"],
            message=result["message"],
            hubspot_url=crm_service.hubspot.get_contact_url(result["contact_id"])
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al agregar nota: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/contact", response_model=ContactUpdateResponse)
async def update_contact(update: ContactUpdate):
    """CASO 3: Actualizar campos de un contacto"""
    try:
        result = await crm_service.update_contact(update)
        
        return ContactUpdateResponse(
            id=result["contact_id"],
            contact_name=result["contact_name"],
            updated_fields=result["updated_fields"],
            message=result["message"],
            hubspot_url=crm_service.hubspot.get_contact_url(result["contact_id"])
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if "campos" in str(e) else status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error al actualizar contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )