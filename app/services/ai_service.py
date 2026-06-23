import os
import json
import logging
from openai import OpenAI
from openai import APIError, RateLimitError

logger = logging.getLogger(__name__)

class IAService:
    def __init__(self):
        """
        Inicializa el cliente de OpenAI.
        Lee la API key de /etc/secrets/OPENAI_API_KEY primero, luego de env vars.
        Esto evita crash en startup si la key no está.
        """
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("Falta OPENAI_API_KEY en /etc/secrets/ o como variable de entorno")
        self.client = OpenAI(api_key=api_key)

    def _get_api_key(self) -> str:
        """
        Busca la API key en 2 lugares:
        1. Secret File de Render: /etc/secrets/OPENAI_API_KEY
        2. Variable de entorno: OPENAI_API_KEY
        """
        # 1. Intenta leer Secret File de Render
        secret_path = "/etc/secrets/OPENAI_API_KEY"
        try:
            if os.path.exists(secret_path):
                with open(secret_path, "r") as f:
                    key = f.read().strip()
                    if key:
                        logger.info("API Key cargada desde Secret File")
                        return key
        except Exception as e:
            logger.warning(f"No se pudo leer Secret File: {e}")

        # 2. Fallback a variable de entorno para desarrollo local
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            logger.info("API Key cargada desde variable de entorno")
            return env_key.strip()

        return None

    def analizar_necesidad(self, texto: str) -> dict:
        """
        Analiza una necesidad del PAA usando OpenAI.
        Devuelve JSON con: analisis, modalidad_sugerida, recomendaciones
        """
        if not texto or len(texto.strip()) < 10:
            return {"error": "La descripción es muy corta. Mínimo 10 caracteres."}

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Eres experto en contratación pública de Colombia: Ley 80 de 1993, Ley 1150 de 2007, Decreto 1082 de 2015.
Analiza necesidades del Plan Anual de Adquisiciones PAA.
Si detectas palabras como 'apoyar', 'acompañamiento', 'asistir', 'demás actividades', evalúa Contratación Directa por prestación de servicios profesionales.
Si detectas 'obra', 'construcción', 'adecuación', 'mantenimiento', evalúa Licitación Pública, Selección Abreviada o Mínima Cuantía según cuantía.
Si detectas 'consultoría', 'estudios', 'diseños', evalúa Concurso de Méritos.
Responde SOLO en JSON válido con estas 3 claves exactas:
1. "analisis": resumen técnico de máximo 3 líneas
2. "modalidad_sugerida": una de [Licitación Pública, Selección Abreviada, Concurso de Méritos, Contratación Directa, Mínima Cuantía]
3. "recomendaciones": array de 2 strings con recomendaciones puntuales para SECOP II"""
                    },
                    {
                        "role": "user",
                        "content": f"Necesidad del PAA a analizar: {texto}"
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                max_tokens=500
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except RateLimitError:
            logger.error("Rate limit de OpenAI alcanzado")
            return {"error": "Límite de consultas alcanzado. Intenta en 1 minuto."}

        except APIError as e:
            logger.error(f"Error de API OpenAI: {e}")
            return {"error": f"Error en servicio de IA: {str(e)}"}

        except json.JSONDecodeError as e:
            logger.error(f"OpenAI no devolvió JSON válido: {e}")
            return {"error": "La IA devolvió respuesta inválida. Intenta de nuevo."}

        except Exception as e:
            logger.error(f"Error inesperado en analizar_necesidad: {e}")
            return {"error": f"Fallo al analizar: {str(e)}"}