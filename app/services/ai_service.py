import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class IAService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Falta OPENAI_API_KEY en variables de entorno")
        self.client = OpenAI(api_key=api_key)

    def analizar_necesidad(self, texto: str) -> dict:
        if len(texto.strip()) < 10:
            return {"error": "La descripción es muy corta para analizar. Mínimo 10 caracteres."}

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres experto en contratación pública de Colombia Ley 80 de 1993, Ley 1150 de 2007.
                        Analiza necesidades del PAA y responde SOLO en JSON con estas 3 claves exactas:
                        1. "analisis": resumen técnico de 2-3 líneas máximo
                        2. "modalidad_sugerida": Licitación Pública, Selección Abreviada, Concurso de Méritos, Contratación Directa o Mínima Cuantía
                        3. "recomendaciones": array de 2 recomendaciones puntuales para SECOP II"""
                    },
                    {
                        "role": "user",
                        "content": f"Necesidad a analizar: {texto}"
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.error(f"Error OpenAI: {e}")
            return {"error": f"Fallo al analizar: {str(e)}"}
