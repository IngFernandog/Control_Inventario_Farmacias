from __future__ import annotations
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class _Nodo(Generic[T]):
    """Nodo interno de la cola enlazada."""

    def __init__(self, dato: T) -> None:
        self.dato: T = dato
        self.siguiente: Optional[_Nodo[T]] = None


class ColaSolicitudes(Generic[T]):
    def __init__(self) -> None:
        self._frente: Optional[_Nodo[T]] = None
        self._final: Optional[_Nodo[T]] = None
        self._tamano: int = 0

    def esta_vacia(self) -> bool:
        return self._tamano == 0

    def __len__(self) -> int:
        return self._tamano

    def encolar(self, objeto: T) -> None:
        if objeto is None:
            raise ValueError("No se puede encolar None.")

        nuevo = _Nodo(objeto)
        if self._final is None:
            self._frente = nuevo
            self._final = nuevo
        else:
            self._final.siguiente = nuevo
            self._final = nuevo
        self._tamano += 1

    def frente(self) -> Optional[T]:
        if self._frente is None:
            return None
        return self._frente.dato

    def desencolar(self) -> Optional[T]:
 
        if self._frente is None:
            return None

        dato = self._frente.dato
        self._frente = self._frente.siguiente
        self._tamano -= 1

        if self._frente is None:
            self._final = None

        return dato