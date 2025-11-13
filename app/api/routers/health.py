from fastapi import APIRouter
from app.api.models import HealthResponse
from app.api.clients.hubspot_client import HubSpotClient
from app.api.config import settings
from datetime import datetime

router = APIRouter()
hubspot = HubSpotClient()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Verifica estado de la API y conexión con HubSpot"""
    hubspot_ok = await hubspot.test_connection()
    
    return HealthResponse(
        status="healthy" if hubspot_ok else "degraded",
        version=settings.APP_VERSION,
        hubspot_connected=hubspot_ok,
        timestamp=datetime.utcnow()
    )