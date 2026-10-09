-- ============================================================
-- PP2 Grupo 10 - Sistema Web de Gestión para Taller de Motos
-- Esquema completo de la base de datos (SOLO ESTRUCTURA, sin datos)
-- Reconstruido a partir de information_schema de la base real.
-- Uso: importar en phpMyAdmin (pestaña Importar) o ejecutar con mysql.
-- Después, crear el usuario de la aplicación desde el sistema/README
-- (esta tabla queda vacía: no contiene credenciales).
-- ============================================================

CREATE DATABASE IF NOT EXISTS pp2_taller_motos
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE pp2_taller_motos;

CREATE TABLE IF NOT EXISTS usuarios (
  id            INT(11)      NOT NULL AUTO_INCREMENT,
  usuario       VARCHAR(50)  NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuarios_usuario (usuario)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clientes (
  id        INT(11)      NOT NULL AUTO_INCREMENT,
  nombre    VARCHAR(100) NOT NULL,
  apellido  VARCHAR(100) NOT NULL,
  telefono  VARCHAR(20)  NOT NULL,
  direccion VARCHAR(200) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS motos (
  id         INT(11)     NOT NULL AUTO_INCREMENT,
  cliente_id INT(11)     NOT NULL,
  patente    VARCHAR(10) NOT NULL,
  marca      VARCHAR(50) NOT NULL,
  modelo     VARCHAR(50) NOT NULL,
  anio       INT(11)     NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_motos_patente (patente),
  KEY idx_motos_cliente (cliente_id),
  CONSTRAINT fk_motos_cliente FOREIGN KEY (cliente_id) REFERENCES clientes (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS servicios (
  id          INT(11)       NOT NULL AUTO_INCREMENT,
  moto_id     INT(11)       NOT NULL,
  fecha       DATE          NOT NULL,
  descripcion VARCHAR(200)  NOT NULL,
  costo       DECIMAL(10,2) NOT NULL,
  ingreso     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado      VARCHAR(20)   NOT NULL DEFAULT 'En proceso',
  retiro      DATETIME      NULL DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_servicios_moto (moto_id),
  CONSTRAINT fk_servicios_moto FOREIGN KEY (moto_id) REFERENCES motos (id)
) ENGINE=InnoDB;
