import os
from openai import OpenAI
from app.core.config import Escenarios

class IAService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en variables de entorno")
        self.client = OpenAI(api_key=api_key)
        self.modelo = "gpt-4o-mini"

    def analizar_necesidad(self, texto: str) -> dict:
        """
        Analiza una necesidad del PAA usando GPT-4o-mini
        """
        try:
            prompt_sistema = f"""
Eres un experto en contratación pública de Colombia.
Analiza la siguiente necesidad del Plan Anual de Adquisiciones PAA.
Devuelve un JSON con 3 claves:
1. "analisis": resumen de 2 líneas de la necesidad
2. "recomendaciones": lista de 3 recomendaciones técnicas específicas
3. "modalidad_sugerida": una de estas opciones {Escenarios.LICITACION_PUBLICA}, {Escenarios.SELECCION_ABREVIADA}, {Escenarios.MINIMA_CUANTIA}, {Escenarios.CONTRATACION_DIRECTA}

Solo responde el JSON, sin texto adicional.
"""

            response = self.client.chat**Vamos a conectar OpenAI real. 2 commits:**

### **Commit 1: `chore: add openai dependency`**

**1. En GitHub, crea/edita `requirements.txt` en la raíz del repo**
`Add file` → `Create new file` → nombre: `requirements.txt`

Pega esto:
