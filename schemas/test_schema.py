from schemas.necesidad import NecesidadPAAInput
from pydantic import ValidationError

try:
    data = NecesidadPAAInput(
        dependencia="secretaria general",
        objeto="Compra de computadores portatiles",
        valor=50_000_000,
        mes="Marzo"
    )
    print("Válido:", data.model_dump())
except ValidationError as e:
    print(e)

# Prueba que falle
try:
    NecesidadPAAInput(dependencia="", objeto="x", valor=-5, mes="Marz0")
except ValidationError as e:
    print("Error esperado:\n", e)