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
            timeout=15.0, # Subí a 15s por si Groq está lento
            max_retries=2
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
                        "content": self._system_prompt()
                    },
                    {
                        "role": "user",
                        "content": self._build_prompt(necesidad)
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1 # Más bajo = respuestas más consistentes
            )
            data = json.loads(r.choices[0].message.content)
            data.update(necesidad.to_dict())
            data["motor_ia"] = f"Groq {settings.ia_model}"
            return data
        except Exception as e:
            logging.error(f"Error Groq: {e}. Fallback local.")
            return self._analisis_local(necesidad)

    def _system_prompt(self) -> str:
        return """
        Eres un experto en contratación estatal Colombia y clasificador UNSPSC v14.
        Tu única tarea es devolver un JSON válido con 4 claves exactas.
        No agregues texto, explicaciones ni markdown. Solo JSON.
        """

    def _build_prompt(self, n: NecesidadPAA) -> str:
        return f"""
        Clasifica esta necesidad del Plan Anual de Adquisiciones PAA Colombia.

        SMMLV 2026 = ${settings.smmlv_2026:,}
        Valor en SMMLV = {n.valor / settings.smmlv_2026:.1f}

        DATOS:
        Dependencia: {n.dependencia}
        Objeto: {n.objeto}
        Valor: ${n.valor:,}
        Mes: {n.mes}

        INSTRUCCIONES:
        1. codigo_unspsc: Busca el código UNSPSC de 8 dígitos más específico para el BIEN o SERVICIO principal.
           Ejemplos: computadores=43211503, impresoras=43212105, licencias software=43232300,
           mantenimiento computadores=81112200, consultoría=80101500
           NO uses códigos genéricos como 71123000 a menos que realmente sea "servicios de adquisición".

        2. modalidad_recomendada: Según Ley 80/1993:
           - Valor <= 28 SMMLV: "Mínima Cuantía"
           - Valor > 28 y <= 182 SMMLV: "Selección Abreviada de Menor Cuantía"
           - Valor > 182 SMMLV: "Licitación Pública"

        3. riesgos: "Alto", "Medio" o "Bajo" según valor y complejidad. >182 SMMLV = Alto.

        4. justificacion: Explica en 1 línea la modalidad elegida citando el valor en SMMLV y la Ley 80.

        Responde SOLO este JSON:
        {{
          "codigo_unspsc": "string 8 dígitos",
          "modalidad_recomendada": "string",
          "riesgos": "string",
          "justificacion": "string"
        }}
        """

    def _analisis_local(self, n: NecesidadPAA) -> Dict[str, Any]:
        smmlv = settings.smmlv_2026
        if n.valor <= 28 * smmlv:
            modalidad = "Mínima Cuantía"
        elif n.valor <= 182 * smmlv:
            modalidad = "Selección Abreviada de Menor Cuantía"
        else:
            modalidad = "Licitación Pública"

        # Fallback con UNSPSC básico por palabra clave
        objeto_lower = n.objeto.lower()
        if "computador" in objeto_lower or "pc" in objeto_lower:
            unspsc = "43211503"
        elif "impresora" in objeto_lower:
            unspsc = "43212105"
        elif "software" in objeto_lower or "licencia" in objeto_lower:
            unspsc = "43232300"
        else:
            unspsc = "43211507"

        return {
            "codigo_unspsc": unspsc,
            "modalidad_recomendada": modalidad,
            "riesgos": "Alto" if n.valor > 182*smmlv else "Medio",
            "justificacion": f"Fallback local. Valor {n.valor/smmlv:.1f} SMMLV = {modalidad}",
            **n.to_dict(),
            "motor_ia": "Fallback local"
        }