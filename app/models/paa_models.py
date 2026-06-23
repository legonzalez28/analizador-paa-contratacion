from pydantic import BaseModel
from typing import Optional

class NecesidadPAA(BaseModel):
    descripcion: str
    valor_estimado: Optional[float] = None
    modalidad: Optional[str] = None
    mes_inicio: Optional[str] = None
