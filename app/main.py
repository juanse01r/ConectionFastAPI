from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.config import settings
from app.api.routers import crm, health
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Crear app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para gestionar contactos en HubSpot via n8n"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, tags=["Health"])
app.include_router(crm.router, tags=["CRM"])


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "CRM Integration API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "create_contact": "POST /crm/contact",
            "add_note": "POST /crm/contact/note",
            "update_contact": "PATCH /crm/contact"
        }
    }