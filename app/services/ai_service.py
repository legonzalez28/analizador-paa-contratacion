import os
from openai import OpenAI

class IAService:
    def __init__(self):
        # Usa la API key de las variables de entorno de Render
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.modelo = "gpt-4o-mini"

    def analizar_necesidad(self, texto: str) -> dict:
        """Analiza una necesidad del PAA y devuelve clasificación"""
        try:
            response = self.client.chat.completions.create(
**Aquí tienes código base para cada archivo. Copia-pega tal cual en GitHub con `Add file`.**

### **1. `app/services/ai_service.py`**
Crea el archivo y pega esto:
```python
class IAService:
    def __init__(self):
        pass

    def analizar_necesidad(self, texto: str) -> dict:
        """
        Analiza una necesidad del PAA y devuelve sugerencias.
        """
        return {
            "analisis": f"Análisis para: {texto}",
            "recomendaciones": ["Definir objeto claro", "Revisar código UNSPSC"]
        }
