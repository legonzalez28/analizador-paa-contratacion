import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class IAService:
    def __init__(self):
        """
        Inicializa el servicio. Si MODO_OFFLINE=true, usa mocks.
        Si no, valida que exista OPENAI_API_KEY y crea el cliente.
        """
        self.modo_offline = os.getenv("MODO_OFFLINE", "false").lower() == "true"

        if self.modo_offline:
            logger.info("IAService iniciado en MODO_OFFLINE. Usando respuestas mock.")
            self.client = None
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Falta OPENAI_API_KEY en variables de entorno")
            self.client = OpenAI(api_key=api_key)
            logger.info("IAService iniciado con OpenAI gpt-4o-mini.")

    def _analizar_con_mock(self, texto: str) -> dict:
        """
        Respuesta simulada para desarrollo sin gastar tokens.
        """
        logger.info(f"Generando respuesta MOCK para: {texto[:40]}...")

        # Lógica simple para que el mock se vea real
        modalidad = "Licitación Pública"
        if "50" in texto or "menor" in texto.lower():
            modalidad = "Selección Abreviada de Menor Cuantía"
        if "software" in texto.lower() or "licencia" in texto.lower():
            modalidad = "Contratación Directa"

        return {
            "analisis": f"""[MOCK] Análisis para: {texto}

1. Objeto sugerido: {texto}. Verificar especificaciones técnicas en estudios previos.
2. Modalidad probable: {modalidad}. Validar cuantía contra presupuesto 2026 y SMMLV.
3. Riesgos clave:
   - Estudios de mercado desactualizados
   - Falta de pluralidad de oferentes
   - Incumplimiento de cronograma PAA
4. Recomendaciones SECOP II:
   - Publicar en Plan Anual de Adquisiciones
   - Usar pliegos tipo si aplica
   - Verificar código UNSPSC correcto""",
            "modelo_usado": "mock-offline-v1",
            "modalidad_sugerida": modalidad,
            "recomendaciones": [
                "Validar en SECOP II",
                "Revisar Manual de Contratación de la entidad",
                "Confirmar disponibilidad presupuestal CDP"
            ],
            "estado": "ok"
        }

    def _analizar_con_openai(self, texto: str) -> dict:
        """
        Llama a la API real de OpenAI.
        """
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("IA_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "Eres experto en contratación pública Colombia. Analiza necesidades PAA. Entrega: 1. Objeto sugerido, 2. Modalidad probable según cuantía y Decreto 1082/2015, 3. Riesgos clave, 4. Recomendaciones para SECOP II."
                    },
                    {
                        "role": "user",
                        "content": f"Analiza esta necesidad del PAA: {texto}"
                    }
                ],
                temperature=0.2,
                max_tokens=800
            )
            return {
                "analisis": response.choices[0].message.content,
                "modelo_usado": "gpt-4o-mini",
                "modalidad_sugerida": "Extraída del análisis",
                "recomendaciones": ["Ver análisis completo"],
                "estado": "ok"
            }
        except Exception as e:
            logger.error(f"Error llamando a OpenAI: {e}")
            # Capturamos errores específicos de OpenAI
            if "rate_limit" in str(e).lower():
                return {"error": "Límite de consultas alcanzado. Intenta en 1 minuto."}
            if "insufficient_quota" in str(e).lower():
                return {"error": "Sin saldo en cuenta OpenAI. Verificar facturación."}
            if "invalid_api_key" in str(e).lower():
                return {"error": "API Key de OpenAI inválida."}
            return {"error": f"Error del proveedor IA: {str(e)}"}

    def analizar_necesidad(self, texto: str) -> dict:
        """
        Punto de entrada principal. Decide si usar mock o OpenAI real.
        """
        if self.modo_offline:
            return self._analizar_con_mock(texto)
        else:
            return self._analizar_con_openai(texto)        