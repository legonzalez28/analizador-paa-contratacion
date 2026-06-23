import os

class Settings:
    PROJECT_NAME: str = "Analizador PAA Contratacion"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()

class Escenarios:
    """Constantes de escenarios de contratación"""
    LICITACION_PUBLICA = "Licitación Pública"
    SELECCION_ABREVIADA = "Selección Abreviada"
    MINIMA_CUANTIA = "Mínima Cuantía"
    CONTRATACION_DIRECTA = "Contratación Directa"
