
-- ============================================================
-- GRUPO 07 - CONTROL DE INVENTARIO DE FARMACIAS
-- Base de datos: MySQL Server 8.0
-- Archivo: sql/esquema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS control_inventario_farmacias
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE control_inventario_farmacias;

-- ============================================================
-- 1. MEDICAMENTOS
-- ============================================================

CREATE TABLE IF NOT EXISTS medicamentos (
    id_medicamento VARCHAR(64) NOT NULL,
    denominacion VARCHAR(255) NOT NULL,

    PRIMARY KEY (id_medicamento),

    CONSTRAINT chk_medicamento_denominacion
        CHECK (CHAR_LENGTH(TRIM(denominacion)) > 0)
) ENGINE=InnoDB;

-- ============================================================
-- 2. SEDES
-- ============================================================

CREATE TABLE IF NOT EXISTS sedes (
    id VARCHAR(64) NOT NULL,

    PRIMARY KEY (id)
) ENGINE=InnoDB;

-- ============================================================
-- 3. LOTES
-- ============================================================

CREATE TABLE IF NOT EXISTS lotes (
    id_lote VARCHAR(64) NOT NULL,
    id_medicamento VARCHAR(64) NOT NULL,
    sede VARCHAR(64) NOT NULL,
    vencimiento DATE NOT NULL,
    cantidad INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    secuencia_alta BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    PRIMARY KEY (id_lote),
    UNIQUE KEY uq_lote_secuencia (secuencia_alta),

    INDEX idx_lote_medicamento_sede
        (id_medicamento, sede),

    INDEX idx_lote_vencimiento
        (vencimiento, id_lote),

    CONSTRAINT fk_lote_medicamento
        FOREIGN KEY (id_medicamento)
        REFERENCES medicamentos(id_medicamento),

    CONSTRAINT fk_lote_sede
        FOREIGN KEY (sede)
        REFERENCES sedes(id),

    CONSTRAINT chk_lote_cantidad
        CHECK (cantidad >= 0)

) ENGINE=InnoDB;

-- ============================================================
-- 4. CONEXIONES
-- ============================================================

CREATE TABLE IF NOT EXISTS conexiones (
    origen VARCHAR(64) NOT NULL,
    destino VARCHAR(64) NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,

    PRIMARY KEY (origen, destino),

    INDEX idx_conexion_destino (destino),

    CONSTRAINT fk_conexion_origen
        FOREIGN KEY (origen)
        REFERENCES sedes(id),

    CONSTRAINT fk_conexion_destino
        FOREIGN KEY (destino)
        REFERENCES sedes(id),

    CONSTRAINT chk_conexion_distinta
        CHECK (origen <> destino)

) ENGINE=InnoDB;

-- ============================================================
-- 5. SOLICITUDES
-- ============================================================

CREATE TABLE IF NOT EXISTS solicitudes (
    id VARCHAR(64) NOT NULL,
    sede VARCHAR(64) NOT NULL,
    medicamento VARCHAR(64) NOT NULL,
    cantidad INT NOT NULL,
    orden BIGINT UNSIGNED NOT NULL,
    atendida BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (id),

    UNIQUE KEY uq_solicitud_orden (orden),

    INDEX idx_solicitud_pendiente
        (atendida, orden),

    CONSTRAINT fk_solicitud_sede
        FOREIGN KEY (sede)
        REFERENCES sedes(id),

    CONSTRAINT fk_solicitud_medicamento
        FOREIGN KEY (medicamento)
        REFERENCES medicamentos(id_medicamento),

    CONSTRAINT chk_solicitud_cantidad
        CHECK (cantidad > 0)

) ENGINE=InnoDB;

-- ============================================================
-- 6. MOVIMIENTOS
-- ============================================================

CREATE TABLE IF NOT EXISTS movimientos (
    id_op VARCHAR(64) NOT NULL,
    id_lote VARCHAR(64) NOT NULL,
    delta INT NOT NULL,
    saldo_anterior INT NOT NULL,
    saldo_posterior INT NOT NULL,

    PRIMARY KEY (id_op),

    INDEX idx_movimiento_lote (id_lote),

    CONSTRAINT fk_movimiento_lote
        FOREIGN KEY (id_lote)
        REFERENCES lotes(id_lote),

    CONSTRAINT chk_movimiento_delta
        CHECK (delta <> 0),

    CONSTRAINT chk_movimiento_saldos
        CHECK (
            saldo_anterior >= 0
            AND saldo_posterior >= 0
            AND saldo_anterior + delta = saldo_posterior
        )

) ENGINE=InnoDB;

-- ============================================================
-- VERIFICACION DEL ESQUEMA
-- ============================================================

SHOW TABLES;

