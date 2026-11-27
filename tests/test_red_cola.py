import unittest

from src.cola import ColaSolicitudes
from src.grafo import GrafoFarmacias


class TestColaSolicitudes(unittest.TestCase):
    def test_cp09_fifo_y_vaciado_uno_a_cero(self) -> None:
        """CP-09: Encolar S1 y S2, atender en orden FIFO y limpiar frente/final al vaciar."""
        cola: ColaSolicitudes[str] = ColaSolicitudes()

        self.assertTrue(cola.esta_vacia())
        self.assertIsNone(cola.frente())
        self.assertIsNone(cola.desencolar())

        cola.encolar("S1")
        cola.encolar("S2")
        self.assertEqual(len(cola), 2)
        self.assertEqual(cola.frente(), "S1")

        # Primera atención: sale S1, queda S2 (1 nodo)
        self.assertEqual(cola.desencolar(), "S1")
        self.assertEqual(len(cola), 1)
        self.assertEqual(cola.frente(), "S2")
        self.assertIs(cola._frente, cola._final)

        # Segunda atención: paso de 1 a 0 nodos (se limpian frente y final)
        self.assertEqual(cola.desencolar(), "S2")
        self.assertTrue(cola.esta_vacia())
        self.assertEqual(len(cola), 0)
        self.assertIsNone(cola.frente())
        self.assertIsNone(cola._frente)
        self.assertIsNone(cola._final)

    def test_encolar_none_lanza_error(self) -> None:
        cola: ColaSolicitudes[str] = ColaSolicitudes()
        with self.assertRaises(ValueError):
            cola.encolar(None) 


class TestGrafoFarmacias(unittest.TestCase):
    def test_cp10_bloqueo_simetrico_y_bfs(self) -> None:
        red = GrafoFarmacias()
        for sede in ("A", "B", "C"):
            red.agregar_sede(sede)
        red.conectar("A", "B")
        red.conectar("B", "C")

        self.assertEqual(red.bfs("A"), ["A", "B", "C"])

        # Bloquear B-C debe eliminar el enlace en ambos sentidos
        bloqueado = red.bloquear("B", "C")
        self.assertTrue(bloqueado)
        self.assertNotIn("C", red.vecinos("B"))
        self.assertNotIn("B", red.vecinos("C"))

        # Reevaluación tras bloqueo
        self.assertEqual(red.bfs("A"), ["A", "B"])
        self.assertEqual(red.bfs("C"), ["C"])
        self.assertEqual(red.aisladas(), ["C"])

        # Bloquear de nuevo un enlace ya inexistente devuelve False
        self.assertFalse(red.bloquear("B", "C"))

    def test_cp11_deteccion_sedes_aisladas(self) -> None:
        red = GrafoFarmacias()
        for sede in ("A", "B", "C"):
            red.agregar_sede(sede)
        red.conectar("A", "B")

        self.assertEqual(red.aisladas(), ["C"])
        self.assertEqual(red.bfs("C"), ["C"])
        self.assertEqual(red.dfs("C"), ["C"])

    def test_ciclo_y_equivalencia_alcanzables_bfs_dfs(self) -> None:

        red = GrafoFarmacias()
        for sede in ("A", "B", "C", "D"):
            red.agregar_sede(sede)
        red.conectar("A", "B")
        red.conectar("B", "C")
        red.conectar("C", "A")  # Ciclo

        recorrido_bfs = red.bfs("A")
        recorrido_dfs = red.dfs("A")

        self.assertEqual(len(recorrido_bfs), 3)
        self.assertEqual(len(recorrido_dfs), 3)
        self.assertEqual(set(recorrido_bfs), {"A", "B", "C"})
        self.assertEqual(set(recorrido_dfs), {"A", "B", "C"})
        self.assertEqual(red.aisladas(), ["D"])

    def test_errores_controlados(self) -> None:
        """Sede desconocida lanza KeyError; lazo lanza ValueError."""
        red = GrafoFarmacias()
        red.agregar_sede("A")

        with self.assertRaises(KeyError):
            red.bfs("Z")
        with self.assertRaises(KeyError):
            red.dfs("Z")
        with self.assertRaises(KeyError):
            red.conectar("A", "Z")
        with self.assertRaises(ValueError):
            red.conectar("A", "A")


if __name__ == "__main__":
    unittest.main()