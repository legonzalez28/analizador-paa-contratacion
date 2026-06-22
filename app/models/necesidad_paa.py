# models/necesidad_paa.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class NecesidadPAA:
    dependencia: str
    objeto: str
    valor: int
    mes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dependencia": self.dependencia,
            "objeto": self.objeto,
            "valor": self.valor,
            "mes": self.mes
        }