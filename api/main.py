from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.ai_service import IAService

app = FastAPI()
ia_service = IAService()

class NecesidadRequest(BaseModel):
    descripcion: str

@app.post("/analizar")
def analizar_necesidad(request: NecesidadRequest):
    resultado = ia_service.analizar_necesidad(request.descripcion)
    if "error" in resultado:
        raise HTTPException(status_code=400, detail=resultado["error"])
    return resultado
