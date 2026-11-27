"""Operaciones equivalentes para EXP-01; medir.py controla el cronometraje.

    indice = construir_hash(medicamentos)
    resultados = buscar_hash(indice, ids_consulta)

La construcción queda fuera de la medición de búsqueda. Se dimensiona la tabla
para una carga próxima a 0.5 en todos los tamaños, sin crecimiento durante carga.
"""

from collections.abc import Iterable, Sequence

from src.hash import HashMedicamentos
from src.modelos import Medicamento


def construir_hash(medicamentos: Sequence[Medicamento]) -> HashMedicamentos[Medicamento]:
    indice = HashMedicamentos[Medicamento](capacidad=2 * len(medicamentos) + 1)
    for medicamento in medicamentos:
        indice.insertar(medicamento.id_medicamento, medicamento)
    return indice


def construir_lista(medicamentos: Sequence[Medicamento]) -> list[Medicamento]:
    return list(medicamentos)


def buscar_hash(indice: HashMedicamentos[Medicamento], ids: Iterable[str]
                ) -> list[Medicamento | None]:
    return [indice.buscar(id_medicamento) for id_medicamento in ids]


def buscar_lista(medicamentos: Sequence[Medicamento], ids: Iterable[str]
                 ) -> list[Medicamento | None]:
    resultados: list[Medicamento | None] = []
    for id_medicamento in ids:
        encontrado = None
        for medicamento in medicamentos:
            if medicamento.id_medicamento == id_medicamento:
                encontrado = medicamento
                break
        resultados.append(encontrado)
    return resultados
