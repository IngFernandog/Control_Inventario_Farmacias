"""Registros comunes del inventario simulado.

El gestor valida referencias e identifica operaciones repetidas. Los índices
conservan referencias al mismo Lote y el gestor controla sus cambios de saldo.
"""

from dataclasses import dataclass
from datetime import date


def _texto(valor: str, campo: str) -> str:
    if not isinstance(valor, str):
        raise TypeError(f"{campo} debe ser texto")
    if not valor.strip():
        raise ValueError(f"{campo} no puede estar vacío")
    return valor.strip()


def _entero(valor: int, campo: str, minimo: int = 0) -> int:
    if type(valor) is not int:
        raise TypeError(f"{campo} debe ser un entero")
    if valor < minimo:
        raise ValueError(f"{campo} debe ser mayor o igual a {minimo}")
    return valor


@dataclass(frozen=True)
class Medicamento:
    id_medicamento: str
    denominacion: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "id_medicamento", _texto(self.id_medicamento, "id_medicamento"))
        object.__setattr__(self, "denominacion", _texto(self.denominacion, "denominacion"))


@dataclass(frozen=True)
class Sede:
    id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _texto(self.id, "id de sede"))


class Lote:
    """Identidad y clave cronológica fijas; saldo y estado validados.

    vencimiento debe llegar convertido a date desde la capa de carga/UI.
    La secuencia de alta pertenece al gestor y se entrega al heap por separado.
    """

    def __init__(self, id_lote: str, id_medicamento: str, sede: str,
                 vencimiento: date, cantidad: int, activo: bool = True) -> None:
        self._id_lote = _texto(id_lote, "id_lote")
        self._id_medicamento = _texto(id_medicamento, "id_medicamento")
        self._sede = _texto(sede, "sede")
        if type(vencimiento) is not date:
            raise TypeError("vencimiento debe ser una fecha date")
        self._vencimiento = vencimiento
        self.cantidad = cantidad
        self.activo = activo

    @property
    def id_lote(self) -> str:
        return self._id_lote

    @property
    def id_medicamento(self) -> str:
        return self._id_medicamento

    @property
    def sede(self) -> str:
        return self._sede

    @property
    def vencimiento(self) -> date:
        return self._vencimiento

    @property
    def clave(self) -> tuple[date, str]:
        return self._vencimiento, self._id_lote

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        self._cantidad = _entero(valor, "cantidad")

    @property
    def activo(self) -> bool:
        return self._activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        if type(valor) is not bool:
            raise TypeError("activo debe ser bool")
        self._activo = valor

    def __repr__(self) -> str:
        return (f"Lote({self.id_lote!r}, {self.id_medicamento!r}, {self.sede!r}, "
                f"{self.vencimiento.isoformat()}, cantidad={self.cantidad}, activo={self.activo})")


@dataclass(frozen=True)
class Movimiento:
    """Operación aplicada; los intentos rechazados se registran en el gestor."""

    id_op: str
    id_lote: str
    delta: int
    saldo_anterior: int
    saldo_posterior: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "id_op", _texto(self.id_op, "id_op"))
        object.__setattr__(self, "id_lote", _texto(self.id_lote, "id_lote"))
        if type(self.delta) is not int:
            raise TypeError("delta debe ser entero")
        if self.delta == 0:
            raise ValueError("delta debe ser distinto de cero")
        _entero(self.saldo_anterior, "saldo_anterior")
        _entero(self.saldo_posterior, "saldo_posterior")
        if self.saldo_anterior + self.delta != self.saldo_posterior:
            raise ValueError("los saldos no coinciden con el movimiento")


@dataclass(frozen=True)
class Solicitud:
    id: str
    sede: str
    medicamento: str
    cantidad: int
    orden: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _texto(self.id, "id de solicitud"))
        object.__setattr__(self, "sede", _texto(self.sede, "sede"))
        object.__setattr__(self, "medicamento", _texto(self.medicamento, "medicamento"))
        _entero(self.cantidad, "cantidad solicitada", minimo=1)
        _entero(self.orden, "orden")
