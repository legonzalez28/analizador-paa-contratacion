# services/ai_service.py
from __future__ import annotations
import json
import logging
import socket
from typing import Dict, Any
from groq import Groq, APIConnectionError

socket.has_ipv6 = False

from core.config import settings
from models.necesidad_paa import NecesidadPAA

class IAService:
    def __init__(self):
        self.client = Groq(
            api_key=settings.groq_api_key,
            timeout=10.0,
            max_retries=1
        )
    
    def analizar_necesidad(self, necesidad: NecesidadPAA) -> Dict[str, Any]:
        if settings.modo_offline:
            return self._analisis_local(necesidad)
        
        try:
            r = self.client.chat.completions.create(
                model=settings.ia_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un asistente que responde únicamente en formato json válido."
                    },
                    {
                        "role": "user", 
                        "content": self._build_prompt(necesidad)
                    }
                ],
                response_format={"type": "json_object"},
                temperature=settings.ia_temperature
            )
            data = json.loads(r.choices[0].message.content)
            data.update(necesidad.to_dict())
            data["motor_ia"] = f"Groq {settings.ia_model}"
            return data
        except APIConnectionError:
            logging.warning("Groq no disponible. Fallback local.")
            return self._analisis_local(necesidad)

    def _build_prompt(self, n: NecesidadPAA) -> str:
        return f"""
        Eres experto en contratación estatal Colombia Ley 80/1993.
        SMMLV 2026 = ${settings.smmlv_2026:,}
        
        Responde SOLO en formato json con estas claves exactas:
        codigo_unspsc, modalidad_recomendada, riesgos, justificacion
        
        Necesidad a analizar:
        Dependencia: {n.dependencia}
        Objeto: {n.objeto}
        Valor: ${n.valor:,}
        Mes: {n.mes}
        
        Reglas: Mínima <=28 SMMLV, Menor Cuantía <=182 SMMLV, Licitación >182 SMMLV
        """

    def _analisis_local(self, n: NecesidadPAA) -> Dict[str, Any]:
        smmlv = settings.smmlv_2026
        if n.valor <= 28 * smmlv:
            modalidad = "Mínima Cuantía"
        elif n.valor <= 182 * smmlv:
            modalidad = "Selección Abreviada"
        else:
            modalidad = "Licitación Pública"
        
        return {
            "codigo_unspsc": "43211507",
            "modalidad_recomendada": modalidad,
            **n.to_dict(),
            "motor_ia": "Fallback local"
        }