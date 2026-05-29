-- Tabla para los Acuerdos principales
CREATE TABLE acuerdos (
    id INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL
);

-- Tabla para las Áreas vinculadas a los acuerdos
CREATE TABLE areas (
    id INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    acuerdo_id INT,
    pagina_informe INT, -- Útil para referenciar el documento físico
    FOREIGN KEY (acuerdo_id) REFERENCES acuerdos(id)
);

-- Inserción de datos maestros
INSERT INTO acuerdos (id, nombre) VALUES 
(1, 'ACUERDO PARA GOBIERNO PARTICIPATIVO Y TRANSFORMADOR'),
(2, 'ACUERDO PARA EL BIENESTAR Y PROSPERIDAD DEL PUEBLO');

INSERT INTO areas (nombre, acuerdo_id, pagina_informe) VALUES 
('Seguridad Pública', 1, 13),
('Conciliación Municipal', 1, 18),
('Secretaría General Municipal', 1, 20),
('Planeación y Evaluación', 1, 22),
('Transparencia', 1, 26),
('Desarrollo para Pueblos Indígenas', 1, 27),
('Registro del Estado Familiar', 1, 28),
('Sistema DIF Municipal', 2, 33),
('Unidad Básica de Rehabilitación (UBR)', 2, 39),
('Enlace de Salud', 2, 41),
('Traslados', 2, 43),
('Instancia Municipal para el Desarrollo de las mujeres', 2, 45),
('Psicología', 2, 46),
('SIPINNA', 2, 49),
('PILARES', 2, 51),
('Consejo Municipal del Deporte (COMUDE)', 2, 52),
('Despacho de Presidencia', 2, 58);
