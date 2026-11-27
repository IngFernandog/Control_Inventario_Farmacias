from __future__ import annotations
from typing import Dict, List, Set

from src.cola import ColaSolicitudes


class GrafoFarmacias:
    def __init__(self) -> None:
        self._adyacencia: Dict[str, List[str]] = {}

    def _validar_sede_existe(self, id_sede: str) -> None:
        if not isinstance(id_sede, str) or not id_sede.strip():
            raise ValueError("El ID de la sede debe ser una cadena no vacía.")
        if id_sede not in self._adyacencia:
            raise KeyError(f"Sede desconocida: '{id_sede}'.")

    def sedes(self) -> List[str]:
        return list(self._adyacencia.keys())

    def vecinos(self, id_sede: str) -> List[str]:
        self._validar_sede_existe(id_sede)
        return list(self._adyacencia[id_sede])

    def agregar_sede(self, id_sede: str) -> None:
        if not isinstance(id_sede, str) or not id_sede.strip():
            raise ValueError("El ID de la sede debe ser una cadena no vacía.")
        id_limpio = id_sede.strip()
        if id_limpio not in self._adyacencia:
            self._adyacencia[id_limpio] = []

    def conectar(self, a: str, b: str) -> None:
        self._validar_sede_existe(a)
        self._validar_sede_existe(b)
        if a == b:
            raise ValueError(f"No se permiten lazos en la misma sede: '{a}'.")

        if b not in self._adyacencia[a]:
            self._adyacencia[a].append(b)
            self._adyacencia[b].append(a)

    def bloquear(self, a: str, b: str) -> bool:

        self._validar_sede_existe(a)
        self._validar_sede_existe(b)

        if b in self._adyacencia[a]:
            self._adyacencia[a].remove(b)
            self._adyacencia[b].remove(a)
            return True
        return False

    def bfs(self, id_origen: str) -> List[str]:

        self._validar_sede_existe(id_origen)

        visitados: Set[str] = {id_origen}
        orden: List[str] = []
        cola: ColaSolicitudes[str] = ColaSolicitudes()
        cola.encolar(id_origen)

        while not cola.esta_vacia():
            actual = cola.desencolar()
            assert actual is not None
            orden.append(actual)

            for vecino in self._adyacencia[actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.encolar(vecino)

        return orden

    def dfs(self, id_origen: str) -> List[str]:
    
        self._validar_sede_existe(id_origen)

        visitados: Set[str] = set()
        orden: List[str] = []
        pila: List[str] = [id_origen]

        while pila:
            actual = pila.pop()
            if actual in visitados:
                continue
            visitados.add(actual)
            orden.append(actual)

            for vecino in reversed(self._adyacencia[actual]):
                if vecino not in visitados:
                    pila.append(vecino)

        return orden

    def aisladas(self) -> List[str]:
        """Devuelve los IDs de las sedes con grado cero (sin enlaces). O(V)."""
        return [sede for sede, vecinos in self._adyacencia.items() if len(vecinos) == 0]