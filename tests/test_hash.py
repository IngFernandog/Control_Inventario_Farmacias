import sys
import unittest
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experimentos.comparar_hash import construir_hash, construir_lista, buscar_hash, buscar_lista
from src.hash import HashMedicamentos
from src.modelos import Lote, Medicamento, Movimiento, Sede, Solicitud


class TestModelos(unittest.TestCase):
    def test_modelos_y_movimiento_valido(self):
        self.assertEqual(Medicamento(" M1 ", " Simulado ").id_medicamento, "M1")
        self.assertEqual(Sede(" A ").id, "A")
        self.assertEqual(Solicitud("S1", "A", "M1", 2, 1).cantidad, 2)
        self.assertEqual(Movimiento("OP1", "L1", -2, 5, 3).saldo_posterior, 3)
        with self.assertRaises(ValueError):
            Movimiento("OP1", "L1", -2, 5, 4)
        with self.assertRaises(ValueError):
            Movimiento("OP1", "L1", 0, 5, 5)
        with self.assertRaises(ValueError):
            Solicitud("S1", "A", "M1", 0, 1)
        with self.assertRaises(ValueError):
            Medicamento("", "Simulado")

    def test_lote_valida_saldo_estado_y_fecha(self):
        lote = Lote("L1", "M1", "A", date(2027, 1, 10), 5)
        for cantidad, error in [(-1, ValueError), (True, TypeError), (2.5, TypeError)]:
            with self.subTest(cantidad=cantidad):
                with self.assertRaises(error):
                    lote.cantidad = cantidad
                self.assertEqual(lote.cantidad, 5)
        with self.assertRaises(ValueError):
            Lote("L2", "M1", "A", date(2027, 1, 10), -1)
        with self.assertRaises(TypeError):
            Lote("L2", "M1", "A", "2027-01-10", 1)
        with self.assertRaises(TypeError):
            lote.activo = 1
        for campo, valor in [("id_lote", "L2"), ("id_medicamento", "M2"),
                             ("sede", "B"), ("vencimiento", date(2028, 1, 1))]:
            with self.subTest(campo=campo):
                with self.assertRaises(AttributeError):
                    setattr(lote, campo, valor)


class TestHash(unittest.TestCase):
    def test_colision_duplicado_y_ausencia(self):
        tabla = HashMedicamentos[Medicamento](capacidad=3)
        primero = Medicamento("M1", "Uno")
        segundo = Medicamento("M4", "Cuatro")
        self.assertEqual(tabla._indice("M1"), tabla._indice("M4"))
        tabla.insertar("M1", primero)
        tabla.insertar("M4", segundo)
        self.assertIs(tabla.buscar("M1"), primero)
        self.assertIs(tabla.buscar("M4"), segundo)
        with self.assertRaises(ValueError):
            tabla.insertar("M1", Medicamento("M1", "Otro"))
        self.assertEqual(len(tabla), 2)
        self.assertIs(tabla.buscar("M1"), primero)
        self.assertIsNone(tabla.buscar("M99"))

    def test_crecimiento_conserva_identidad_y_cantidad(self):
        tabla = HashMedicamentos[Medicamento](capacidad=3)
        registros = [Medicamento(f"M{i}", f"Simulado {i}") for i in range(200)]
        for registro in registros:
            tabla.insertar(registro.id_medicamento, registro)
        self.assertGreater(tabla.capacidad, 3)
        self.assertEqual(len(tabla), 200)
        self.assertLessEqual(tabla.factor_carga(), 0.75)
        for registro in registros:
            self.assertIs(tabla.buscar(registro.id_medicamento), registro)

    def test_indices_separados_y_lote_compartido(self):
        medicamentos = HashMedicamentos[Medicamento]()
        lotes = HashMedicamentos[Lote]()
        medicamento = Medicamento("M1", "Simulado")
        lote = Lote("L1", "M1", "A", date(2027, 1, 10), 5)
        medicamentos.insertar("M1", medicamento)
        lotes.insertar("L1", lote)
        lote.cantidad = 0
        lote.activo = False
        self.assertIs(lotes.buscar("L1"), lote)
        self.assertEqual(lotes.buscar("L1").cantidad, 0)
        self.assertFalse(lotes.buscar("L1").activo)
        self.assertIsNone(medicamentos.buscar("L1"))

    def test_entradas_invalidas(self):
        with self.assertRaises(TypeError):
            HashMedicamentos(True)
        with self.assertRaises(ValueError):
            HashMedicamentos(0)
        tabla = HashMedicamentos()
        with self.assertRaises(ValueError):
            tabla.insertar("M1", None)
        with self.assertRaises(ValueError):
            tabla.buscar(" ")
        with self.assertRaises(TypeError):
            tabla.buscar(1)

    def test_comparador_presencias_y_ausencias(self):
        registros = [Medicamento(f"M{i}", f"Simulado {i}") for i in range(100)]
        tabla = construir_hash(registros)
        lista = construir_lista(registros)
        consultas = ["M0", "M99", "M500", "M0"]
        por_hash = buscar_hash(tabla, consultas)
        por_lista = buscar_lista(lista, consultas)
        for a, b in zip(por_hash, por_lista):
            self.assertIs(a, b)
        self.assertIs(por_hash[0], registros[0])
        self.assertIsNone(por_hash[2])


if __name__ == "__main__":
    unittest.main(verbosity=2)
