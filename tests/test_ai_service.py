import unittest

from models import NecesidadPAA
from services.ai_service import IAService


class TestIAService(unittest.TestCase):
    def test_analizar_necesidad_returns_expected_fields(self) -> None:
        necesidad = NecesidadPAA(
            dependencia="Secretaría General",
            objeto="Compra de computadores",
            valor=50_000_000,
            mes="Marzo",
        )

        servicio = IAService()
        resultado = servicio.analizar_necesidad(necesidad)

        self.assertIn("codigo_unspsc", resultado)
        self.assertIn("modalidad_recomendada", resultado)
        self.assertIn("riesgos", resultado)


if __name__ == "__main__":
    unittest.main()
