from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.ai_service import IAService  # <- CAMBIO AQUÍ
from app.models.paa_models import NecesidadPAA
from app.core.config import settings

app = FastAPI(title="Analizador PAA Contratación")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ia_service = IAService()

@app.post("/analizar")
async def analizar_necesidad(necesidad: NecesidadPAA):
    try:
        resultado = ia_service.analizar_necesidad(necesidad)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "ok", "model": settings.ia_model}