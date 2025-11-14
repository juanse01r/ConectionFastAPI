from app.api.clients.hubspot_client import HubSpotClient
from app.api.models import ContactCreate, NoteCreate, ContactUpdate
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CRMService:
    """Servicio con lógica de negocio para operaciones CRM"""
    
    def __init__(self):
        self.hubspot = HubSpotClient()
    
    def _get_full_name(self, props: dict) -> str:
        """Obtiene nombre completo de un contacto"""
        firstname = props.get("firstname", "")
        lastname = props.get("lastname", "")
        return f"{firstname} {lastname}".strip() or "Sin nombre"
    
    async def find_contact(self, identifier: str) -> Dict:
        """Encuentra un contacto por email o ID"""
        if "@" in identifier:
            contact = await self.hubspot.search_by_email(identifier)
            if not contact:
                raise ValueError(f"Contacto no encontrado con email: {identifier}")
            return contact
        
        try:
            return await self.hubspot.get_by_id(identifier)
        except:
            raise ValueError(f"Contacto no encontrado con ID: {identifier}")
    
    async def create_contact_with_idempotency(self, contact: ContactCreate) -> Dict:
        """Crea un contacto con idempotencia"""
        logger.info(f"Intentando crear contacto: {contact.email}")
        
        # IDEMPOTENCIA: Verificar si existe
        existing = await self.hubspot.search_by_email(contact.email)
        
        if existing:
            logger.info(f"Contacto ya existe: {existing['id']}")
            props = existing.get("properties", {})
            
            return {
                "contact": existing,
                "message": f"El contacto {self._get_full_name(props)} ya existía en HubSpot",
                "already_existed": True
            }
        
        # Crear nuevo
        properties = {"email": contact.email}
        if contact.firstname:
            properties["firstname"] = contact.firstname
        if contact.lastname:
            properties["lastname"] = contact.lastname
        if contact.phone:
            properties["phone"] = contact.phone
        
        new_contact = await self.hubspot.create_contact(properties)
        props = new_contact.get("properties", {})
        
        logger.info(f"Contacto creado exitosamente: {new_contact['id']}")
        
        return {
            "contact": new_contact,
            "message": f"Contacto {self._get_full_name(props)} creado exitosamente",
            "already_existed": False
        }
    
    async def add_note_to_contact(self, note: NoteCreate) -> Dict:
        """Agrega una nota a un contacto"""
        logger.info(f"Agregando nota a: {note.contact_identifier}")
        
        # PASO 1: Validar que el contacto existe
        try:
            contact = await self.find_contact(note.contact_identifier)
        except Exception as e:
            # Si find_contact lanza excepción, propagar como ValueError para 404
            raise ValueError(f"Contacto no encontrado con identificador: {note.contact_identifier}")
        
        # PASO 2: Validar que hay contenido
        if not note.content or len(note.content.strip()) == 0:
            raise ValueError("El contenido de la nota es obligatorio")
        
        # PASO 3: Crear la nota
        contact_id = contact["id"]
        props = contact.get("properties", {})
        contact_name = self._get_full_name(props)
        
        new_note = await self.hubspot.create_note(note.content)
        note_id = new_note["id"]
        
        await self.hubspot.associate_note_to_contact(note_id, contact_id)
        
        logger.info(f"Nota {note_id} agregada al contacto {contact_id}")
        
        return {
            "note_id": note_id,
            "contact_id": contact_id,
            "contact_name": contact_name,
            "message": f"Nota agregada exitosamente al contacto {contact_name}"
        }
    
    async def update_contact(self, update: ContactUpdate) -> Dict:
        """Actualiza campos de un contacto"""
        logger.info(f"Actualizando contacto: {update.contact_identifier}")
        
        contact = await self.find_contact(update.contact_identifier)
        contact_id = contact["id"]
        props = contact.get("properties", {})
        contact_name = self._get_full_name(props)
        
        # Helper para validar valores reales
        def is_valid_value(value):
            if value is None:
                return False
            if isinstance(value, str) and value.strip().lower() in ['', 'empty', 'null', 'none']:
                return False
            return True
        
        # Construir properties solo con campos que tienen valor real
        properties = {}
        if is_valid_value(update.firstname):
            properties["firstname"] = update.firstname
        if is_valid_value(update.lastname):
            properties["lastname"] = update.lastname
        if is_valid_value(update.phone):
            properties["phone"] = update.phone
        if is_valid_value(update.lifecyclestage):
            properties["lifecyclestage"] = update.lifecyclestage
        
        if not properties:
            raise ValueError("No se especificaron campos para actualizar")
        
        await self.hubspot.update_contact(contact_id, properties)
        
        logger.info(f"Contacto {contact_id} actualizado: {list(properties.keys())}")
        
        fields_updated = ", ".join(properties.keys())
        
        return {
            "contact_id": contact_id,
            "contact_name": contact_name,
            "updated_fields": properties,
            "message": f"Contacto {contact_name} actualizado exitosamente. Campos: {fields_updated}"
        }