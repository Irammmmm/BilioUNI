-- Secuencias para IDs autoincrementales
CREATE SEQUENCE usuarios_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE libros_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE prestamos_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE autores_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE editoriales_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE sanciones_seq START WITH 1 INCREMENT BY 1;

-- Tablas principales
CREATE TABLE usuarios (
    id_usuario NUMBER PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL,
    fecha_registro DATE DEFAULT SYSDATE,
    correo VARCHAR2(100) UNIQUE,
    tipo_usuario VARCHAR2(20) CHECK (tipo_usuario IN ('estudiante', 'profesor', 'administrador'))
);

CREATE TABLE autores (
    id_autor NUMBER PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL
);

CREATE TABLE editoriales (
    id_editorial NUMBER PRIMARY KEY,
    nombre VARCHAR2(100) NOT NULL
);

CREATE TABLE libros (
    id_libro NUMBER PRIMARY KEY,
    titulo VARCHAR2(200) NOT NULL,
    disponible NUMBER(1) DEFAULT 1,
    id_autor NUMBER REFERENCES autores(id_autor),
    id_editorial NUMBER REFERENCES editoriales(id_editorial),
    isbn VARCHAR2(20) UNIQUE,
    anio_publicacion NUMBER(4),
    CONSTRAINT chk_disponible CHECK (disponible IN (0, 1))
);

CREATE TABLE prestamos (
    id_prestamo NUMBER PRIMARY KEY,
    id_usuario NUMBER REFERENCES usuarios(id_usuario),
    id_libro NUMBER REFERENCES libros(id_libro),
    fecha_prestamo DATE DEFAULT SYSDATE,
    fecha_devolucion DATE,
    estado VARCHAR2(20) DEFAULT 'activo'
);

CREATE TABLE sanciones (
    id_sancion NUMBER PRIMARY KEY,
    id_usuario NUMBER REFERENCES usuarios(id_usuario),
    motivo VARCHAR2(200) NOT NULL,
    fecha DATE DEFAULT SYSDATE,
    fecha_fin DATE,
    estado VARCHAR2(20) DEFAULT 'activo'
);

-- Vistas útiles
CREATE VIEW vista_libros_disponibles AS
SELECT l.id_libro, l.titulo, a.nombre AS autor, e.nombre AS editorial
FROM libros l
JOIN autores a ON l.id_autor = a.id_autor
JOIN editoriales e ON l.id_editorial = e.id_editorial
WHERE l.disponible = 1;

-- Procedimientos almacenados
CREATE OR REPLACE PROCEDURE registrar_devolucion(
    p_id_prestamo IN NUMBER,
    p_resultado OUT VARCHAR2
) AS
BEGIN
    UPDATE prestamos 
    SET fecha_devolucion = SYSDATE, 
        estado = 'completado'
    WHERE id_prestamo = p_id_prestamo;
    
    UPDATE libros
    SET disponible = 1
    WHERE id_libro = (SELECT id_libro FROM prestamos WHERE id_prestamo = p_id_prestamo);
    
    p_resultado := 'Devolución registrada correctamente';
EXCEPTION
    WHEN OTHERS THEN
        p_resultado := 'Error: ' || SQLERRM;
END;
/