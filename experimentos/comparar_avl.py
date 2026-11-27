"""EXP-03: construcción AVL/BST con los mismos lotes y convención de altura.

medir.py debe preparar los lotes antes de medir y construir un árbol nuevo en
cada repetición. Altura, inorden y validaciones se consultan fuera del tiempo
de construcción. El BST es totalmente iterativo para soportar claves ordenadas.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from src.avl import ArbolLotes, ClaveLote, validar_clave
from src.modelos import Lote


@dataclass
class NodoBST:
    lote: Lote
    izquierdo: "NodoBST | None" = None
    derecho: "NodoBST | None" = None


class BSTLotes:
    """BST sin balanceo. Vacío tiene altura 0 y hoja 1.

    Inserción/búsqueda O(h); construcción ordenada O(n²), inorden O(n).
    """

    def __init__(self) -> None:
        self._raiz: NodoBST | None = None

    def insertar(self, lote: Lote) -> None:
        if not isinstance(lote, Lote):
            raise TypeError("insertar espera un Lote")
        nuevo = NodoBST(lote)
        if self._raiz is None:
            self._raiz = nuevo
            return
        actual = self._raiz
        clave = lote.clave
        while True:
            if clave == actual.lote.clave:
                raise ValueError(f"clave de lote duplicada: {clave}")
            if clave < actual.lote.clave:
                if actual.izquierdo is None:
                    actual.izquierdo = nuevo
                    return
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = nuevo
                    return
                actual = actual.derecho

    def buscar(self, clave: ClaveLote) -> Lote | None:
        clave = validar_clave(clave)
        actual = self._raiz
        while actual is not None:
            if clave == actual.lote.clave:
                return actual.lote
            if clave < actual.lote.clave:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        return None

    def en_orden(self) -> list[Lote]:
        resultado: list[Lote] = []
        pila: list[NodoBST] = []
        actual = self._raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo
            actual = pila.pop()
            resultado.append(actual.lote)
            actual = actual.derecho
        return resultado

    @property
    def altura(self) -> int:
        if self._raiz is None:
            return 0
        maxima = 0
        pila = [(self._raiz, 1)]
        while pila:
            nodo, nivel = pila.pop()
            maxima = max(maxima, nivel)
            if nodo.izquierdo is not None:
                pila.append((nodo.izquierdo, nivel + 1))
            if nodo.derecho is not None:
                pila.append((nodo.derecho, nivel + 1))
        return maxima


def construir_avl(lotes: Iterable[Lote]) -> ArbolLotes:
    arbol = ArbolLotes()
    for lote in lotes:
        arbol.insertar(lote)
    return arbol


def construir_bst(lotes: Iterable[Lote]) -> BSTLotes:
    arbol = BSTLotes()
    for lote in lotes:
        arbol.insertar(lote)
    return arbol
