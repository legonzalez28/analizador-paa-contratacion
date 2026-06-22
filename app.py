# app.py
from core.config import settings
from models import NecesidadPAA
from app.services.ai_service import IAService

def main():
    n = NecesidadPAA(
        dependencia="Sistemas",
        objeto="Compra de 10 computadores",
        valor=300_000_000,
        mes="Junio"
    )
    servicio = IAService()
    resultado = servicio.analizar_necesidad(n)
    print(resultado)

if __name__ == "__main__":
    main()