import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.ai_service import IAService

# Configurar logs para ver en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Analizador PAA Contratación",
    description="API que analiza necesidades del Plan Anual de Adquisiciones usando IA",
    version="1.0.0"
)

# CORS para que puedas probar desde el navegador o Postman
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NecesidadRequest(BaseModel):
    descripcion: str

class NecesidadResponse(BaseModel):
    analisis: str | None = None
    modalidad_sugerida: str | None = None
    recomendaciones: list[str] | None = None
    error: str | None = None

# NO crear IAService global. Usamos Depends para lazy loading.
def get_ia_service() -> IAService:
    """
    Dependency injection para IAService.
    Se crea solo cuando llega un request a /analizar.
    Si falla la key, devuelve 500 en vez de tumbar toda la app.
    """
    try:
        return IAService()
    except ValueError as e:
        logger.error(f"Fallo al inicializar IAService: {e}")
        raise HTTPException(
            status_code=503,
            detail="Servicio de IA no disponible: falta OPENAI_API_KEY"
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear IAService: {e}")
        raise HTTPException(
            status_code=503,
            detail="Servicio de IA no disponible temporalmente"
        )

@app.get("/")
def health_check():
    """
    Endpoint de salud para Render.
    Render lo usa para saber si el servicio está vivo.
    """
    openai_key_loaded = False
    try:
        # Verificamos si existe sin crear el cliente
        if os.path.exists("/etc/secrets/OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"):
            openai_key_loaded = True
    except:
        pass

    return {
        "status": "ok",
        "service": "analizador-paa-contratacion",
        "openai_key_loaded": openai_key_loaded
    }

@app.post("/analizar", response_model=NecesidadResponse)
def analizar_necesidad(
    request: NecesidadRequest,
    ia_service: IAService = Depends(get_ia_service)
):
    """
    Analiza una necesidad del PAA y devuelve modalidad sugerida.
    """
    logger.info(f"Analizando necesidad: {request.descripcion[:50]}...")

    resultado = ia_service.analizar_necesidad(request.descripcion)

    if "error" in resultado:
        logger.warning(f"Error en análisis: {resultado['error']}")
        raise HTTPException(status_code=400, detail=resultado["error"])

    logger.info("Análisis completado exitosamente")
    return resultado

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log simple de cada request para debug en Render
    """
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response