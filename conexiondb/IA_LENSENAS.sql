-- Crear base de datos
DROP DATABASE IF EXISTS IA_LENSENAS;
CREATE DATABASE IA_LENSENAS;

USE IA_LENSENAS;

-- Crear tabla Roles
CREATE TABLE Roles (
    RolID INT IDENTITY(1,1) PRIMARY KEY,      -- ID único para cada rol
    NombreRol NVARCHAR(50) NOT NULL,          -- Nombre del rol (Administrador, Docente, Alumno)
    Descripcion NVARCHAR(255) NULL            -- Descripción opcional del rol
);

-- Insertar roles
INSERT INTO Roles (NombreRol, Descripcion) VALUES
('Administrador', 'Rol con acceso completo'),
('Maestro', 'Rol para profesores'),
('Estudiante', 'Rol para alumnos');

-- Crear tabla Usuarios
CREATE TABLE Usuarios (
    UsuarioID INT IDENTITY(1,1) PRIMARY KEY,  -- ID único para cada usuario
    Nombre NVARCHAR(50) NOT NULL,              -- Nombre del usuario
    Apellido NVARCHAR(50) NOT NULL,            -- Apellido del usuario
    Direccion NVARCHAR(255),                   -- Dirección del usuario
    CorreoElectronico NVARCHAR(100) UNIQUE NOT NULL, -- Correo electrónico único
    Telefono NVARCHAR(15),                     -- Número de teléfono
    RolID INT NOT NULL,                        -- Clave foránea que se relaciona con Roles
    FOREIGN KEY (RolID) REFERENCES Roles(RolID) ON DELETE CASCADE
);

-- Crear tabla Inicio de Sesión
CREATE TABLE InicioDeSesion (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    UsuarioID INT NOT NULL,                   -- Clave foránea que se relaciona con Usuarios
    Email VARCHAR(255) NOT NULL UNIQUE,
    Contraseña VARCHAR(255) NOT NULL,
    FechaCreacion DATETIME DEFAULT GETDATE(),  -- Fecha de creación
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(UsuarioID) ON DELETE CASCADE
);

-- Crear tabla Maestro (opcional)
CREATE TABLE Maestro (
    Id INT IDENTITY(1,1) PRIMARY KEY,        -- ID único para cada registro
    Nombre NVARCHAR(50) NOT NULL,            -- Nombre de la persona
    Apellido NVARCHAR(50) NOT NULL,          -- Apellido de la persona
    Direccion NVARCHAR(255) NOT NULL,        -- Dirección de la persona
    CorreoElectronico NVARCHAR(100) NOT NULL, -- Correo electrónico de la persona
    Telefono NVARCHAR(20) NOT NULL,          -- Teléfono de la persona
    Especialidad NVARCHAR(100),              -- Especialidad de la persona (opcional)
    FechaNacimiento DATE NOT NULL,           -- Fecha de nacimiento
    Genero NVARCHAR(10) NOT NULL             -- Género (Masculino/Femenino)
);

-- Crear tabla Estudiantes
CREATE TABLE Estudiantes (
    EstudianteID INT PRIMARY KEY IDENTITY(1,1),
    Nombre NVARCHAR(100) NOT NULL,
    Apellido NVARCHAR(100) NOT NULL,
    Direccion NVARCHAR(255),
    CorreoElectronico NVARCHAR(100) UNIQUE,
    Telefono NVARCHAR(15),
    FechaNacimiento DATE,
    Genero NVARCHAR(10)
);

-- Crear tabla Archivos
CREATE TABLE Archivos (
    ArchivoID INT IDENTITY(1,1) PRIMARY KEY,         -- ID único para cada archivo
    NombreArchivo NVARCHAR(255) NOT NULL,            -- Nombre del archivo
    RutaArchivo NVARCHAR(255) NOT NULL,              -- Ruta del archivo en el servidor
    EstudianteID INT NOT NULL,                        -- ID del estudiante que puede ver el archivo
    FechaSubida DATETIME DEFAULT GETDATE(),          -- Fecha en que se subió el archivo
    FOREIGN KEY (EstudianteID) REFERENCES Estudiantes(EstudianteID) ON DELETE CASCADE
);

-- Inserción de usuarios
INSERT INTO Usuarios (Nombre, Apellido, Direccion, CorreoElectronico, Telefono, RolID) VALUES
('Admin', 'Admin', 'Direccion Admin', 'admin@example.com', '123456789', 1),  -- Administrador
('Maestro', 'Maestro', 'Direccion Maestro', 'maestro@example.com', '987654321', 2),  -- Maestro
('Estudiante', 'Estudiante', 'Direccion Estudiante', 'estudiante@example.com', '555555555', 3);  -- Estudiante

-- Inserción de usuarios con diferentes roles en Inicio de Sesión
INSERT INTO InicioDeSesion (UsuarioID, Email, Contraseña) VALUES 
(1, 'admin@example.com', 'contraseñaAdmin'),  -- Administrador
(2, 'maestro@example.com', 'contraseñaMaestro'),  -- Maestro
(3, 'estudiante@example.com', 'contraseñaEstudiante');  -- Estudiante


select * from InicioDeSesion


/*select * from InicioDeSesion*/

/*
admin@example.com	contraseñaAdmin
maestro@example.com	contraseñaMaestro
estudiante@example.com	contraseñaEstudiante*/
