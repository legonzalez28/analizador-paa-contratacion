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
            timeout=15.0,
            max_retries=2
        )

    def analizar_necesidad(self, necesidad: NecesidadPAA) -> Dict[str, Any]:
        if settings.modo_offline:
            return self._analisis_local(necesidad)

        try:
            r = self.client.chat.completions.create(
                model=settings.ia_model,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": self._build_prompt(necesidad)}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            data = json.loads(r.choices[0].message.content)
            data.update(necesidad.to_dict())
            data["motor_ia"] = f"Groq {settings.ia_model}"
            return data
        except Exception as e:
            logging.error(f"Error Groq: {e}. Usando fallback local.")
            return self._analisis_local(necesidad)

    def _system_prompt(self) -> str:
        return """
        Eres un clasificador experto en UNSPSC v14 para Colombia Compra Eficiente.
        Tu única tarea es devolver un JSON válido con 4 claves exactas.
        No agregues texto, explicaciones ni markdown. Solo JSON.
        """

    def _build_prompt(self, n: NecesidadPAA) -> str:
        smmlv = settings.smmlv_2026
        valor_smmlv = n.valor / smmlv

        return f"""
        Clasifica esta necesidad del Plan Anual de Adquisiciones PAA Colombia.

        SMMLV 2026 = ${smmlv:,}
        Valor = ${n.valor:,} = {valor_smmlv:.1f} SMMLV

        DATOS:
        Dependencia: {n.dependencia}
        Objeto: {n.objeto}
        Valor: ${n.valor:,}
        Mes: {n.mes}

        INSTRUCCIONES ESTRICTAS:
        1. codigo_unspsc: Código UNSPSC de 8 dígitos del BIEN o SERVICIO PRINCIPAL.
           Usa estos ejemplos:
           - computadores, portátiles, PC = 43211503
           - impresoras, escáneres = 43212105
           - licencias software, Office 365 = 43232300
           - mantenimiento computadores = 81112200
           - consultoría = 80101500
           - servicio aseo = 76111501
           PROHIBIDO usar 71123000 "Servicios de adquisición" salvo que el objeto sea literalmente eso.

        2. modalidad_recomendada: Según Ley 80/1993:
           - Valor <= 28 SMMLV: "Mínima Cuantía"
           - Valor > 28 y <= 182 SMMLV: "Selección Abreviada de Menor Cuantía"
           - Valor > 182 SMMLV: "Licitación Pública"

        3. riesgos: "Alto", "Medio" o "Bajo". Si valor > 182 SMMLV = "Alto".

        4. justificacion: Una línea explicando la modalidad con el valor en SMMLV.

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
        valor_smmlv = n.valor / smmlv

        if n.valor <= 28 * smmlv:
            modalidad = "Mínima Cuantía"
            riesgo = "Bajo"
        elif n.valor <= 182 * smmlv:
            modalidad = "Selección Abreviada de Menor Cuantía"
            riesgo = "Medio"
        else:
            modalidad = "Licitación Pública"
            riesgo = "Alto"

        # Fallback UNSPSC por palabra clave - NO LO BORRES
        obj = n.objeto.lower()
        if any(w in obj for w in ["computador", "portatil", "pc", "laptop"]):
            unspsc = "43211503"
        elif any(w in obj for w in ["impresora", "escaner", "scanner"]):
            unspsc = "43212105"
        elif any(w in obj for w in ["software", "licencia", "office", "antivirus"]):
            unspsc = "43232300"
        elif any(w in obj for w in ["mantenimiento", "soporte"]):
            unspsc = "81112200"
        elif any(w in obj for w in ["consultoria", "asesoria"]):
            unspsc = "80101500"
        elif any(w in obj for w in ["aseo", "cafeteria", "limpieza"]):
            unspsc = "76111501"
        else:
            unspsc = "43211507"

        return {
            "codigo_unspsc": unspsc,
            "modalidad_recomendada": modalidad,
            "riesgos": riesgo,
            "justificacion": f"Fallback local. Valor {valor_smmlv:.1f} SMMLV = {modalidad}",
            **n.to_dict(),
            "motor_ia": "Fallback local"
        }