
"""
GRUPO 07 - CONTROL DE INVENTARIO DE FARMACIAS
Archivo: src/persistencia.py
Responsable: Harold

Conexion, almacenamiento y recuperacion de datos en MySQL.
"""

import pymysql

from src.modelos import Medicamento, Sede, Lote, Movimiento, Solicitud


class PersistenciaMySQL:

    # --------------------------------------------------------
    # 1. CONEXION A MYSQL
    # --------------------------------------------------------

    def __init__(self, host="localhost", usuario="root",
                 password="", puerto=3306):

        self.host = host
        self.usuario = usuario
        self.password = password
        self.puerto = puerto
        self.base_datos = "control_inventario_farmacias"

    def conectar(self):
        conexion = pymysql.connect(
            host=self.host,
            user=self.usuario,
            password=self.password,
            port=self.puerto,
            database=self.base_datos,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )

        return conexion

    def comprobar_conexion(self):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT VERSION() AS version")
            resultado = cursor.fetchone()
            cursor.close()

            return resultado["version"]

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 2. MEDICAMENTOS
    # --------------------------------------------------------

    def guardar_medicamento(self, medicamento):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            sql = """
                INSERT INTO medicamentos
                (id_medicamento, denominacion)
                VALUES (%s, %s)
            """

            datos = (
                medicamento.id_medicamento,
                medicamento.denominacion
            )

            cursor.execute(sql, datos)
            conexion.commit()
            cursor.close()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def buscar_medicamento(self, id_medicamento):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            sql = """
                SELECT id_medicamento, denominacion
                FROM medicamentos
                WHERE id_medicamento = %s
            """

            cursor.execute(sql, (id_medicamento,))
            fila = cursor.fetchone()
            cursor.close()

            if fila is None:
                return None

            medicamento = Medicamento(
                fila["id_medicamento"],
                fila["denominacion"]
            )

            return medicamento

        finally:
            conexion.close()

    def listar_medicamentos(self):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id_medicamento, denominacion
                FROM medicamentos
                ORDER BY id_medicamento
            """)

            filas = cursor.fetchall()
            cursor.close()

            medicamentos = []

            for fila in filas:
                medicamento = Medicamento(
                    fila["id_medicamento"],
                    fila["denominacion"]
                )
                medicamentos.append(medicamento)

            return medicamentos

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 3. SEDES
    # --------------------------------------------------------

    def guardar_sede(self, sede):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            sql = "INSERT INTO sedes (id) VALUES (%s)"
            cursor.execute(sql, (sede.id,))

            conexion.commit()
            cursor.close()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def listar_sedes(self):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id FROM sedes ORDER BY id")
            filas = cursor.fetchall()
            cursor.close()

            sedes = []

            for fila in filas:
                sede = Sede(fila["id"])
                sedes.append(sede)

            return sedes

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 4. LOTES
    # --------------------------------------------------------

    def guardar_lote(self, lote):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            sql = """
                INSERT INTO lotes
                (id_lote, id_medicamento, sede,
                 vencimiento, cantidad, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            datos = (
                lote.id_lote,
                lote.id_medicamento,
                lote.sede,
                lote.vencimiento,
                lote.cantidad,
                lote.activo
            )

            cursor.execute(sql, datos)

            secuencia = cursor.lastrowid

            conexion.commit()
            cursor.close()

            return secuencia

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def buscar_lote(self, id_lote):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            sql = "SELECT * FROM lotes WHERE id_lote = %s"
            cursor.execute(sql, (id_lote,))

            fila = cursor.fetchone()
            cursor.close()

            if fila is None:
                return None

            lote = Lote(
                fila["id_lote"],
                fila["id_medicamento"],
                fila["sede"],
                fila["vencimiento"],
                fila["cantidad"],
                bool(fila["activo"])
            )

            return lote

        finally:
            conexion.close()

    def listar_lotes(self):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT * FROM lotes
                ORDER BY vencimiento, id_lote
            """)

            filas = cursor.fetchall()
            cursor.close()

            lotes = []

            for fila in filas:
                lote = Lote(
                    fila["id_lote"],
                    fila["id_medicamento"],
                    fila["sede"],
                    fila["vencimiento"],
                    fila["cantidad"],
                    bool(fila["activo"])
                )

                secuencia = fila["secuencia_alta"]
                lotes.append((lote, secuencia))

            return lotes

        finally:
            conexion.close()

    def cambiar_estado_lote(self, id_lote, activo):
        if type(activo) is not bool:
            raise TypeError("El estado debe ser booleano")

        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            sql = """
                UPDATE lotes
                SET activo = %s
                WHERE id_lote = %s
            """

            cursor.execute(sql, (activo, id_lote))

            if cursor.rowcount == 0:
                raise ValueError("Lote inexistente o sin cambios")

            conexion.commit()
            cursor.close()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 5. MOVIMIENTOS DE INVENTARIO
    # --------------------------------------------------------

    def registrar_movimiento(self, id_op, id_lote, delta):

        if type(delta) is not int or delta == 0:
            raise ValueError("Movimiento invalido")

        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            # Verificar si la operacion ya existe
            cursor.execute("""
                SELECT id_op
                FROM movimientos
                WHERE id_op = %s
            """, (id_op,))

            if cursor.fetchone() is not None:
                raise ValueError("Operacion duplicada")

            # Bloquear el lote mientras se modifica
            cursor.execute("""
                SELECT cantidad, activo
                FROM lotes
                WHERE id_lote = %s
                FOR UPDATE
            """, (id_lote,))

            fila = cursor.fetchone()

            if fila is None:
                raise ValueError("Lote inexistente")

            if not fila["activo"]:
                raise ValueError("Lote inactivo")

            saldo_anterior = fila["cantidad"]
            saldo_posterior = saldo_anterior + delta

            if saldo_posterior < 0:
                raise ValueError("Stock insuficiente")

            # Validar el objeto del movimiento
            movimiento = Movimiento(
                id_op,
                id_lote,
                delta,
                saldo_anterior,
                saldo_posterior
            )

            # Actualizar el saldo
            cursor.execute("""
                UPDATE lotes
                SET cantidad = %s
                WHERE id_lote = %s
            """, (saldo_posterior, id_lote))

            # Guardar el movimiento
            cursor.execute("""
                INSERT INTO movimientos
                (id_op, id_lote, delta,
                 saldo_anterior, saldo_posterior)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                movimiento.id_op,
                movimiento.id_lote,
                movimiento.delta,
                movimiento.saldo_anterior,
                movimiento.saldo_posterior
            ))

            conexion.commit()
            cursor.close()

            return movimiento

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def listar_movimientos(self):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT id_op, id_lote, delta,
                       saldo_anterior, saldo_posterior
                FROM movimientos
                ORDER BY id_op
            """)

            filas = cursor.fetchall()
            cursor.close()

            movimientos = []

            for fila in filas:
                movimiento = Movimiento(
                    fila["id_op"],
                    fila["id_lote"],
                    fila["delta"],
                    fila["saldo_anterior"],
                    fila["saldo_posterior"]
                )
                movimientos.append(movimiento)

            return movimientos

        finally:
            conexion.close()

    def consultar_stock(self, id_medicamento, sede):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                SELECT SUM(cantidad) AS total
                FROM lotes
                WHERE id_medicamento = %s
                AND sede = %s
                AND activo = TRUE
            """, (id_medicamento, sede))

            fila = cursor.fetchone()
            cursor.close()

            if fila["total"] is None:
                return 0

            return int(fila["total"])

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 6. SOLICITUDES
    # --------------------------------------------------------

    def guardar_solicitud(self, solicitud):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO solicitudes
                (id, sede, medicamento, cantidad, orden, atendida)
                VALUES (%s, %s, %s, %s, %s, FALSE)
            """, (
                solicitud.id,
                solicitud.sede,
                solicitud.medicamento,
                solicitud.cantidad,
                solicitud.orden
            ))

            conexion.commit()
            cursor.close()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def listar_solicitudes(self, solo_pendientes=True):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            if solo_pendientes:
                cursor.execute("""
                    SELECT * FROM solicitudes
                    WHERE atendida = FALSE
                    ORDER BY orden, id
                """)
            else:
                cursor.execute("""
                    SELECT * FROM solicitudes
                    ORDER BY orden, id
                """)

            filas = cursor.fetchall()
            cursor.close()

            solicitudes = []

            for fila in filas:
                solicitud = Solicitud(
                    fila["id"],
                    fila["sede"],
                    fila["medicamento"],
                    fila["cantidad"],
                    fila["orden"]
                )
                solicitudes.append(solicitud)

            return solicitudes

        finally:
            conexion.close()

    def atender_solicitud(self, id_solicitud):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE solicitudes
                SET atendida = TRUE
                WHERE id = %s AND atendida = FALSE
            """, (id_solicitud,))

            if cursor.rowcount == 0:
                raise ValueError(
                    "Solicitud inexistente o ya atendida"
                )

            conexion.commit()
            cursor.close()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 7. CONEXIONES ENTRE SEDES
    # --------------------------------------------------------

    def guardar_conexion(self, origen, destino):

        if origen == destino:
            raise ValueError("Las sedes deben ser diferentes")

        # Guardar cada enlace una sola vez
        if origen > destino:
            origen, destino = destino, origen

        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO conexiones
                (origen, destino, activa)
                VALUES (%s, %s, TRUE)
                ON DUPLICATE KEY UPDATE activa = TRUE
            """, (origen, destino))

            conexion.commit()
            cursor.close()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def bloquear_conexion(self, origen, destino):

        if origen > destino:
            origen, destino = destino, origen

        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE conexiones
                SET activa = FALSE
                WHERE origen = %s
                AND destino = %s
                AND activa = TRUE
            """, (origen, destino))

            bloqueada = cursor.rowcount == 1

            conexion.commit()
            cursor.close()

            return bloqueada

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def listar_conexiones(self, incluir_bloqueadas=False):
        conexion = self.conectar()

        try:
            cursor = conexion.cursor()

            if incluir_bloqueadas:
                cursor.execute("""
                    SELECT origen, destino, activa
                    FROM conexiones
                    ORDER BY origen, destino
                """)
            else:
                cursor.execute("""
                    SELECT origen, destino, activa
                    FROM conexiones
                    WHERE activa = TRUE
                    ORDER BY origen, destino
                """)

            filas = cursor.fetchall()
            cursor.close()

            return filas

        finally:
            conexion.close()

    # --------------------------------------------------------
    # 8. RECUPERAR LOS DATOS
    # --------------------------------------------------------

    def cargar_estado(self):
        """Recupera todos los datos para reconstruir los TAD."""

        estado = {}

        estado["medicamentos"] = self.listar_medicamentos()
        estado["sedes"] = self.listar_sedes()
        estado["lotes"] = self.listar_lotes()
        estado["solicitudes"] = self.listar_solicitudes()
        estado["conexiones"] = self.listar_conexiones(True)
        estado["movimientos"] = self.listar_movimientos()

        return estado
