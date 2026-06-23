# api main module
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.ai_service import IAService
from app.models.paa_models import NecesidadPAA
from app.core.config import settings

app = FastAPI(title="Analizador PAA Contratacion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ia_service = IAService()
