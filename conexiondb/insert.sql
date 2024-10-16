USE IA_LENSENAS;
-- Insertar roles
INSERT INTO Roles (NombreRol, Descripcion)
VALUES ('Administrador', 'Acceso total al sistema'),
       ('Docente', 'Acceso para gestionar clases y estudiantes'),
       ('Alumno', 'Acceso limitado para ver y completar lecciones');

	   -- Insertar usuarios
INSERT INTO Usuarios (Nombre, Apellido, Direccion, CorreoElectronico, Telefono, RolID)
VALUES ('Lurdes', 'Martínez', '123 Calle Falsa', 'lurdes.martinez@example.com', '555-1234', 1), -- Administrador
       ('Juan', 'García', '456 Calle Verdadera', 'juan.garcia@example.com', '555-5678', 2),     -- Docente
       ('Maria', 'Lopez', '789 Calle Central', 'maria.lopez@example.com', '555-9876', 3);       -- Alumno

	   -- Insertar inicio de sesión
INSERT INTO iniciodesesion (UsuarioID, email, contraseña)
VALUES (1, 'lurdes.martinez@example.com', 'contrasenaSegura1'), -- Lurdes
       (2, 'juan.garcia@example.com', 'contrasenaSegura2'),     -- Juan
       (3, 'maria.lopez@example.com', 'contrasenaSegura3');     -- Maria
