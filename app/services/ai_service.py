class IAService:
    def __init__(self):
        pass

    def analizar_necesidad(self, texto: str) -> dict:
        return {
            "analisis": f"Análisis para: {texto}",
            "recomendaciones": [
                "Definir objeto contractual claro",
                "Revisar código UNSPSC correspondiente"
            ],
            "modalidad_sugerida": "Mínima Cuantía"
        }
