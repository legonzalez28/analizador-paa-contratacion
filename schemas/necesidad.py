# schemas/necesidad.py
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Literal

MESES_VALIDOS = Literal["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

class NecesidadPAAInput(BaseModel):
    dependencia: str = Field(min_length=3, description="Área responsable")
    objeto: str = Field(min_length=10, max_length=500)
    valor: int = Field(gt=0, le=10_000_000_000_000, description="COP")  # <-- CAMBIO: 10.0 mil millones
    mes: MESES_VALIDOS
    
    @field_validator('dependencia', 'objeto')
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('No puede estar vacío o solo espacios')
        return v.strip().title()

    model_config = {"str_strip_whitespace": True}