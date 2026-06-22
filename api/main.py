from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import NecesidadPAA
from services import IAService
from core.config import settings
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI(title="Analizador PAA Contratación Estatal")
servicio = IAService()

class NecesidadRequest(BaseModel):
    dependencia: str
    objeto: str
    valor: int
    mes: str

@app.get("/")
def health():
    return {"status": "ok", "modo_offline": settings.modo_offline}

@app.get("/cuantias/{anio}")
def get_cuantias(anio: int):
    smmlv_dict = {
        2023: 1160000,
        2024: 1300000,
        2025: 1423500,
        2026: 2000000
    }
    if anio not in smmlv_dict:
        raise HTTPException(status_code=404, detail=f"SMMLV para año {anio} no configurado")
    
    smmlv = smmlv_dict[anio]
    minima = 28 * smmlv
    menor = 182 * smmlv
    
    return {
        "anio": anio,
        "smmlv": smmlv,
        "minima_cuantia": {"desde": 0, "hasta": minima},
        "menor_cuantia": {"desde": minima + 1, "hasta": menor},
        "licitacion_publica": {"desde": menor + 1}
    }

@app.post("/analizar")
def analizar_necesidad(request: NecesidadRequest):
    necesidad = NecesidadPAA(**request.model_dump())
    return servicio.analizar_necesidad(necesidad)