"""Índice AVL por (vencimiento, id_lote), con referencias al lote canónico."""

from dataclasses import dataclass
from datetime import date

from .modelos import Lote, _texto

ClaveLote = tuple[date, str]


def validar_clave(clave: ClaveLote) -> ClaveLote:
    if not isinstance(clave, tuple) or len(clave) != 2:
        raise TypeError("la clave debe ser (fecha date, id_lote)")
    fecha, id_lote = clave
    if type(fecha) is not date:
        raise TypeError("la fecha de la clave debe ser date")
    return fecha, _texto(id_lote, "id_lote")


@dataclass
class NodoAVL:
    lote: Lote
    izquierdo: "NodoAVL | None" = None
    derecho: "NodoAVL | None" = None
    altura: int = 1


class ArbolLotes:
    """Inserción/búsqueda O(log n), inorden O(n), memoria O(n).

    Convención de altura: vacío 0, hoja 1. Duplicado de clave genera ValueError.
    Cantidad y estado no alteran la clave y se observan por referencia compartida.
    """

    def __init__(self) -> None:
        self._raiz: NodoAVL | None = None

    @staticmethod
    def _altura(nodo: NodoAVL | None) -> int:
        return 0 if nodo is None else nodo.altura

    @property
    def altura(self) -> int:
        return self._altura(self._raiz)

    def _actualizar_altura(self, nodo: NodoAVL) -> None:
        nodo.altura = 1 + max(self._altura(nodo.izquierdo), self._altura(nodo.derecho))

    def _balance(self, nodo: NodoAVL) -> int:
        return self._altura(nodo.izquierdo) - self._altura(nodo.derecho)

    def _rotar_derecha(self, nodo: NodoAVL) -> NodoAVL:
        nueva_raiz = nodo.izquierdo
        assert nueva_raiz is not None
        nodo.izquierdo = nueva_raiz.derecho
        nueva_raiz.derecho = nodo
        self._actualizar_altura(nodo)
        self._actualizar_altura(nueva_raiz)
        return nueva_raiz

    def _rotar_izquierda(self, nodo: NodoAVL) -> NodoAVL:
        nueva_raiz = nodo.derecho
        assert nueva_raiz is not None
        nodo.derecho = nueva_raiz.izquierdo
        nueva_raiz.izquierdo = nodo
        self._actualizar_altura(nodo)
        self._actualizar_altura(nueva_raiz)
        return nueva_raiz

    def insertar(self, lote: Lote) -> None:
        if not isinstance(lote, Lote):
            raise TypeError("insertar espera un Lote")
        self._raiz = self._insertar(self._raiz, lote)

    def _insertar(self, nodo: NodoAVL | None, lote: Lote) -> NodoAVL:
        if nodo is None:
            return NodoAVL(lote)
        if lote.clave < nodo.lote.clave:
            nodo.izquierdo = self._insertar(nodo.izquierdo, lote)
        elif lote.clave > nodo.lote.clave:
            nodo.derecho = self._insertar(nodo.derecho, lote)
        else:
            raise ValueError(f"clave de lote duplicada: {lote.clave}")

        self._actualizar_altura(nodo)
        balance = self._balance(nodo)
        if balance > 1:
            assert nodo.izquierdo is not None
            if self._balance(nodo.izquierdo) < 0:
                nodo.izquierdo = self._rotar_izquierda(nodo.izquierdo)
            return self._rotar_derecha(nodo)
        if balance < -1:
            assert nodo.derecho is not None
            if self._balance(nodo.derecho) > 0:
                nodo.derecho = self._rotar_derecha(nodo.derecho)
            return self._rotar_izquierda(nodo)
        return nodo

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
        pila: list[NodoAVL] = []
        actual = self._raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo
            actual = pila.pop()
            resultado.append(actual.lote)
            actual = actual.derecho
        return resultado

    def validar_balance(self) -> bool:
        """Comprueba orden global, alturas almacenadas y balance en O(n)."""
        valido, _ = self._revisar(self._raiz, None, None)
        return valido

    def _revisar(self, nodo: NodoAVL | None, minimo: ClaveLote | None,
                 maximo: ClaveLote | None) -> tuple[bool, int]:
        if nodo is None:
            return True, 0
        clave = nodo.lote.clave
        if minimo is not None and clave <= minimo:
            return False, 0
        if maximo is not None and clave >= maximo:
            return False, 0
        valida_i, altura_i = self._revisar(nodo.izquierdo, minimo, clave)
        valida_d, altura_d = self._revisar(nodo.derecho, clave, maximo)
        altura = 1 + max(altura_i, altura_d)
        valido = (valida_i and valida_d and abs(altura_i - altura_d) <= 1
                  and nodo.altura == altura)
        return valido, altura
