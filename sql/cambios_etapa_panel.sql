-- Etapa 1 del panel "Motos en el taller"
-- Ejecutar UNA SOLA VEZ en phpMyAdmin (base pp2_taller_motos, pestana SQL).
-- Agrega a la tabla servicios: hora de ingreso automatica, estado y fecha de retiro.
-- Los servicios cargados antes de este cambio quedan "En proceso" con la hora en que se ejecuta este script.

ALTER TABLE servicios
    ADD COLUMN ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN estado VARCHAR(20) NOT NULL DEFAULT 'En proceso',
    ADD COLUMN retiro DATETIME NULL;
