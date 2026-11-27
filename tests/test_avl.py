import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from experimentos.comparar_avl import BSTLotes, construir_avl, construir_bst
from src.avl import ArbolLotes
from src.hash import HashMedicamentos
from src.modelos import Lote


def crear_lote(id_lote, dia):
    return Lote(id_lote, "M1", "A", date(2027, 1, 1) + timedelta(days=dia - 1), 5)


class TestAVL(unittest.TestCase):
    def test_vacio_y_busqueda_ausente(self):
        arbol = ArbolLotes()
        self.assertEqual(arbol.en_orden(), [])
        self.assertEqual(arbol.altura, 0)
        self.assertTrue(arbol.validar_balance())
        self.assertIsNone(arbol.buscar((date(2027, 1, 1), "L99")))

    def test_cuatro_rotaciones(self):
        for dias in [(30, 20, 10), (10, 20, 30), (30, 10, 20), (10, 30, 20)]:
            with self.subTest(dias=dias):
                arbol = ArbolLotes()
                for dia in dias:
                    arbol.insertar(crear_lote(f"L{dia}", dia))
                    self.assertTrue(arbol.validar_balance())
                self.assertEqual(arbol._raiz.lote.vencimiento.day, 20)
                self.assertEqual(arbol.altura, 2)
                self.assertEqual([l.vencimiento.day for l in arbol.en_orden()], [10, 20, 30])

    def test_cp08_desempate_busqueda_y_duplicado(self):
        lotes = [crear_lote("L2", 10), crear_lote("L1", 10), crear_lote("L3", 9)]
        arbol = construir_avl(lotes)
        self.assertEqual([l.id_lote for l in arbol.en_orden()], ["L3", "L1", "L2"])
        self.assertIs(arbol.buscar(lotes[1].clave), lotes[1])
        with self.assertRaises(ValueError):
            arbol.insertar(crear_lote("L1", 10))
        self.assertEqual(len(arbol.en_orden()), 3)
        self.assertTrue(arbol.validar_balance())

    def test_objeto_compartido_con_hash(self):
        lote = crear_lote("L1", 10)
        tabla = HashMedicamentos[Lote]()
        tabla.insertar(lote.id_lote, lote)
        arbol = construir_avl([lote])
        tabla.buscar("L1").cantidad = 0
        tabla.buscar("L1").activo = False
        encontrado = arbol.buscar(lote.clave)
        self.assertIs(encontrado, lote)
        self.assertEqual(encontrado.cantidad, 0)
        self.assertFalse(encontrado.activo)
        self.assertEqual(arbol.en_orden(), [lote])

    def test_balance_y_orden_global_con_entradas_mezcladas(self):
        lotes = [crear_lote(f"L{i:04d}", i + 1) for i in range(200)]
        random.Random(7).shuffle(lotes)
        arbol = ArbolLotes()
        for lote in lotes:
            arbol.insertar(lote)
            self.assertTrue(arbol.validar_balance())
        self.assertEqual([l.clave for l in arbol.en_orden()], sorted(l.clave for l in lotes))

    def test_detecta_altura_incorrecta_y_orden_fuera_del_subarbol(self):
        arbol = construir_avl([crear_lote("L20", 20), crear_lote("L10", 10),
                              crear_lote("L30", 30), crear_lote("L15", 15)])
        arbol._raiz.altura += 1
        self.assertFalse(arbol.validar_balance())
        arbol._raiz.altura -= 1
        # 25 es mayor que su padre 10, pero viola el límite de la raíz 20.
        arbol._raiz.izquierdo.derecho.lote = crear_lote("L25", 25)
        self.assertFalse(arbol.validar_balance())

    def test_entradas_invalidas(self):
        arbol = ArbolLotes()
        with self.assertRaises(TypeError):
            arbol.insertar(None)
        for clave in [("2027-01-10", "L1"), (date(2027, 1, 10),), "L1"]:
            with self.subTest(clave=clave):
                with self.assertRaises(TypeError):
                    arbol.buscar(clave)


class TestComparacionBST(unittest.TestCase):
    def test_bst_vacio_y_duplicado(self):
        arbol = BSTLotes()
        self.assertEqual((arbol.en_orden(), arbol.altura), ([], 0))
        lote = crear_lote("L1", 1)
        self.assertIsNone(arbol.buscar(lote.clave))
        arbol.insertar(lote)
        self.assertIs(arbol.buscar(lote.clave), lote)
        with self.assertRaises(ValueError):
            arbol.insertar(lote)

    def test_bst_recorrido_con_ambas_ramas(self):
        lotes = [crear_lote(f"L{dia}", dia) for dia in [20, 10, 30, 5, 15]]
        bst = construir_bst(lotes)
        self.assertEqual(bst.altura, 3)
        self.assertEqual(bst.en_orden(), construir_avl(lotes).en_orden())

    def test_claves_ordenadas_superan_la_recursion_sin_cambiar_limite(self):
        limite = sys.getrecursionlimit()
        lotes = [crear_lote(f"L{i:04d}", i + 1) for i in range(1500)]
        avl = construir_avl(lotes)
        bst = construir_bst(lotes)
        self.assertEqual(bst.altura, 1500)
        self.assertEqual(bst.en_orden(), lotes)
        self.assertEqual(avl.en_orden(), lotes)
        self.assertLess(avl.altura, 20)
        self.assertTrue(avl.validar_balance())
        self.assertEqual(sys.getrecursionlimit(), limite)


if __name__ == "__main__":
    unittest.main(verbosity=2)
