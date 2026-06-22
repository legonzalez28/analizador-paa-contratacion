import json
import os
from typing import Dict, Any
from groq import Groq
from app.core.config import settings
from app.models.paa_models import NecesidadPAA

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.modo_offline = settings.modo_offline

    def analizar_necesidad(self, necesidad: NecesidadPAA) -> Dict[str, Any]:
        if self.modo_offline:
            return self._modo_offline(necesidad)

        try:
            # 1. Solo le pedimos a Groq el UNSPSC. El resto lo calculamos nosotros.
            prompt = f"""
Eres un experto en contratación estatal de Colombia.
Devuelve SOLO un JSON válido con esta estructura:

{{
  "codigo_unspsc": "string"
}}

Para este objeto de contratación: "{necesidad.objeto}"
Clasifícalo con el código UNSPSC de 8 dígitos más específico.
No agregues explicaciones, solo el JSON.
"""

            response = self.client.chat.completions.create(
                model=settings.ia_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)

        except Exception as e:
            # Si Groq falla, usa fallback
            print(f"Error Groq: {e}")
            data = {"codigo_unspsc": "43211503"} # default computadores

        # 2. CALCULAMOS NOSOTROS LA MODALIDAD Y RIESGOS - IGNORAMOS AL LLM
        smmlv_valor = necesidad.valor / settings.smmlv_2026
        umbral_minima = 28 * settings.smmlv_2026
        umbral_menor = 182 * settings.smmlv_2026

        if necesidad.valor <= umbral_minima:
            modalidad = "Mínima Cuantía"
            riesgos = "Bajo"
            justificacion = f"Valor de {smmlv_valor:.1f} SMMLV es menor o igual a 28 SMMLV. Según Art. 2 Ley 1150 de 2007, corresponde Mínima Cuantía."
        elif necesidad.valor <= umbral_menor:
            modalidad = "Selección Abreviada de Menor Cuantía"
            riesgos = "Medio"
            justificacion = f"Valor de {smmlv_valor:.1f} SMMLV está entre 28 y 182 SMMLV. Según Ley 80/1993, corresponde Selección Abreviada de Menor Cuantía."
        else:
            modalidad = "Licitación Pública"
            riesgos = "Alto"
            justificacion = f"Valor de {smmlv_valor:.1f} SMMLV supera 182 SMMLV. Según Ley 80/1993, corresponde Licitación Pública."

        # 3. Armamos la respuesta final
        resultado = {
            "codigo_unspsc": data.get("codigo_unspsc", "43211503"),
            "modalidad_recomendada": modalidad,
            "riesgos": riesgos,
            "justificacion": justificacion,
            "dependencia": necesidad.dependencia,
            "objeto": necesidad.objeto,
            "valor": str(necesidad.valor),
            "mes": necesidad.mes,
            "motor_ia": f"Groq {settings.ia_model}"
        }

        return resultado

    def _modo_offline(self, necesidad: NecesidadPAA) -> Dict[str, Any]:
        # Mismo cálculo que arriba pero sin llamar a Groq
        smmlv_valor = necesidad.valor / settings.smmlv_2026

        if necesidad.valor <= 28 * settings.smmlv_2026:
            modalidad = "Mínima Cuantía"
            riesgos = "Bajo"
        elif necesidad.valor <= 182 * settings.smmlv_2026:
            modalidad = "Selección Abreviada de Menor Cuantía"
            riesgos = "Medio"
        else:
            modalidad = "Licitación Pública"
            riesgos = "Alto"

        return {
            "codigo_unspsc": "43211503", # default offline
            "modalidad_recomendada": modalidad,
            "riesgos": riesgos,
            "justificacion": f"Valor de {smmlv_valor:.1f} SMMLV. Cálculo local sin IA.",
            "dependencia": necesidad.dependencia,
            "objeto": necesidad.objeto,
            "valor": str(necesidad.valor),
            "mes": necesidad.mes,
            "motor_ia": "Modo Offline"
        }