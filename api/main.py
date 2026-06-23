import os
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
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
# En prod cambia allow_origins=["https://tu-frontend.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NecesidadRequest(BaseModel):
    descripcion: str = Field(..., min_length=10, max_length=2000, description="Texto de la necesidad del PAA")

class NecesidadResponse(BaseModel):
    analisis: str | None = None
    modelo_usado: str | None = None
    modalidad_sugerida: str | None = None
    recomendaciones: list[str] | None = None
    estado: str | None = None
    error: str | None = None

def get_ia_service() -> IAService:
    """
    Dependency injection para IAService.
    Se crea solo cuando llega un request a /analizar.
    Si falla la key, devuelve 503 en vez de tumbar toda la app.
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
    Endpoint de salud para Render y debug.
    Muestra estado de env vars clave.
    """
    return {
        "status": "ok",
        "service": "analizador-paa-contratacion",
        "env": "render",
        "openai_key_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "modo_offline": os.getenv("MODO_OFFLINE", "false"),
        "ia_model": os.getenv("IA_MODEL", "gpt-4o-mini")
    }

@app.post("/analizar", response_model=NecesidadResponse)
def analizar_necesidad(
    request: NecesidadRequest,
    ia_service: IAService = Depends(get_ia_service)
):
    """
    Analiza una necesidad del PAA y devuelve modalidad sugerida.
    """
    try:
        logger.info(f"Analizando necesidad: {request.descripcion[:50]}...")
        resultado = ia_service.analizar_necesidad(request.descripcion)

        # Si el servicio de IA devolvió error controlado, lo pasamos como 502
        if "error" in resultado:
            logger.warning(f"Error del proveedor IA: {resultado['error']}")
            raise HTTPException(status_code=502, detail=f"Error del proveedor IA: {resultado['error']}")

        logger.info("Análisis completado exitosamente")
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Fallo inesperado en /analizar")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log simple de cada request para debug en Render
    """
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response