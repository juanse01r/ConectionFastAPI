import httpx
from typing import Optional, Dict
from app.api.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Cliente para comunicación con HubSpot API"""
    
    def __init__(self):
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {settings.HUBSPOT_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.timeout = settings.HUBSPOT_TIMEOUT
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Método genérico para requests HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=self.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                error_msg = e.response.json().get("message", str(e)) if e.response.text else str(e)
                logger.error(f"HubSpot error: {error_msg}")
                raise Exception(f"Error de HubSpot: {error_msg}")
            except Exception as e:
                logger.error(f"Request error: {str(e)}")
                raise Exception(f"Error de conexión: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Verifica conexión con HubSpot"""
        try:
            await self._request("GET", "/crm/v3/objects/contacts", params={"limit": 1})
            return True
        except:
            return False
    
    async def search_by_email(self, email: str) -> Optional[Dict]:
        """Busca contacto por email"""
        data = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email
                }]
            }],
            "properties": ["email", "firstname", "lastname", "phone", "lifecyclestage"]
        }
        
        response = await self._request("POST", "/crm/v3/objects/contacts/search", json=data)
        
        if response.get("total", 0) > 0:
            return response["results"][0]
        return None
    
    async def get_by_id(self, contact_id: str) -> Dict:
        """Obtiene contacto por ID"""
        return await self._request(
            "GET",
            f"/crm/v3/objects/contacts/{contact_id}",
            params={"properties": "email,firstname,lastname,phone,lifecyclestage"}
        )
    
    async def create_contact(self, properties: Dict) -> Dict:
        """Crea un contacto"""
        data = {"properties": properties}
        return await self._request("POST", "/crm/v3/objects/contacts", json=data)
    
    async def update_contact(self, contact_id: str, properties: Dict) -> Dict:
        """Actualiza un contacto"""
        data = {"properties": properties}
        return await self._request("PATCH", f"/crm/v3/objects/contacts/{contact_id}", json=data)
    
    async def create_note(self, content: str) -> Dict:
        """Crea una nota"""
        timestamp_ms = str(int(datetime.utcnow().timestamp() * 1000))
        data = {
            "properties": {
                "hs_note_body": content,
                "hs_timestamp": timestamp_ms
            }
        }
        return await self._request("POST", "/crm/v3/objects/notes", json=data)
    
    async def associate_note_to_contact(self, note_id: str, contact_id: str) -> bool:
        """Asocia una nota a un contacto"""
        await self._request(
            "PUT",
            f"/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/note_to_contact"
        )
        return True
    
    def get_contact_url(self, contact_id: str) -> str:
        """Genera URL del contacto en HubSpot"""
        return f"https://app.hubspot.com/contacts/contact/{contact_id}"