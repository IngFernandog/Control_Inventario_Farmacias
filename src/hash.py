"""Tabla hash propia con cadenas enlazadas y acceso por ID completo."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from .modelos import _texto

T = TypeVar("T")


@dataclass
class _NodoHash(Generic[T]):
    clave: str
    registro: T
    siguiente: "_NodoHash[T] | None" = None


class HashMedicamentos(Generic[T]):
    """Dos instancias independientes permiten indexar medicamentos y lotes.

    insertar rechaza duplicados sin sustituir el registro. buscar devuelve el
    objeto original o None. Carga máxima 0.75; crecimiento amortizado.
    Acceso esperado O(1), peor caso O(n); memoria O(m+n).
    """

    def __init__(self, capacidad: int = 101) -> None:
        if type(capacidad) is not int:
            raise TypeError("capacidad debe ser un entero")
        if capacidad < 1:
            raise ValueError("capacidad debe ser positiva")
        self._cubetas: list[_NodoHash[T] | None] = [None] * capacidad
        self._cantidad = 0

    @property
    def capacidad(self) -> int:
        return len(self._cubetas)

    def __len__(self) -> int:
        return self._cantidad

    def factor_carga(self) -> float:
        return self._cantidad / self.capacidad

    def _indice(self, clave: str) -> int:
        # Hash polinómico reproducible, independiente del hash aleatorio de Python.
        valor = 0
        for caracter in clave:
            valor = (31 * valor + ord(caracter)) % self.capacidad
        return valor

    def buscar(self, clave: str) -> T | None:
        clave = _texto(clave, "clave")
        actual = self._cubetas[self._indice(clave)]
        while actual is not None:
            if actual.clave == clave:
                return actual.registro
            actual = actual.siguiente
        return None

    def insertar(self, clave: str, registro: T) -> None:
        clave = _texto(clave, "clave")
        if registro is None:
            raise ValueError("el registro no puede ser None")
        if self.buscar(clave) is not None:
            raise ValueError(f"ID duplicado: {clave}")
        if (self._cantidad + 1) / self.capacidad > 0.75:
            self._redimensionar()
        indice = self._indice(clave)
        self._cubetas[indice] = _NodoHash(clave, registro, self._cubetas[indice])
        self._cantidad += 1

    def _redimensionar(self) -> None:
        anteriores = self._cubetas
        self._cubetas = [None] * (2 * len(anteriores) + 1)
        # Reubica los nodos conservando objetos y cantidad de registros.
        for cabeza in anteriores:
            actual = cabeza
            while actual is not None:
                siguiente = actual.siguiente
                indice = self._indice(actual.clave)
                actual.siguiente = self._cubetas[indice]
                self._cubetas[indice] = actual
                actual = siguiente
