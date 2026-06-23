import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.services.ai_service import IAService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Analizador PAA Contratación",
    description="API que analiza necesidades del Plan Anual de Adquisiciones usando IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NecesidadRequest(BaseModel):
    descripcion: str = Field(..., min_length=10, max_length=2000)

class NecesidadResponse(BaseModel):
    analisis: str | None = None
    modelo_usado: str | None = None
    estado: str | None = None
    error: str | None = None

def get_ia_service() -> IAService:
    try:
        return IAService()
    except ValueError as e:
        logger.error(f"Fallo al inicializar IAService: {e}")
        raise HTTPException(status_code=503, detail="Servicio IA no disponible: falta OPENAI_API_KEY")
    except Exception as e:
        logger.error(f"Error inesperado al crear IAService: {e}")
        raise HTTPException(status_code=503, detail="Servicio IA no disponible temporalmente")

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "analizador-paa-contratacion",
        "openai_key_loaded": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.post("/analizar", response_model=NecesidadResponse)
def analizar_necesidad(
    request: NecesidadRequest,
    ia_service: IAService = Depends(get_ia_service)
):
    try:
        logger.info(f"Analizando: {request.descripcion[:50]}...")
        resultado = ia_service.analizar_necesidad(request.descripcion)
        if "error" in resultado:
            raise HTTPException(status_code=502, detail=f"Error del proveedor IA: {resultado['error']}")
        return resultado
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Fallo inesperado en /analizar")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response