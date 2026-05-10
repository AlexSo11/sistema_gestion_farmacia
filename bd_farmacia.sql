-- Crear base de datos
CREATE DATABASE IF NOT EXISTS farmacia;
USE farmacia;

-- Eliminar tablas
DROP TABLE IF EXISTS almacenes;
DROP TABLE IF EXISTS detalle_ventas;
DROP TABLE IF EXISTS ventas;
DROP TABLE IF EXISTS compras;
DROP TABLE IF EXISTS articulos;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS usuarios;

-- Tabla de usuarios (CON RFC, TELÉFONO Y EMAIL ÚNICOS)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    email VARCHAR(100) UNIQUE,  -- ÚNICO
    telefono VARCHAR(20) UNIQUE,  -- ÚNICO
    rfc VARCHAR(13) UNIQUE,  -- ÚNICO (NUEVO)
    rol ENUM('admin', 'gerente', 'cajero') NOT NULL DEFAULT 'cajero',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de clientes (CON RFC, PUNTOS Y USUARIO QUE REGISTRÓ)
CREATE TABLE IF NOT EXISTS clientes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    rfc VARCHAR(13) UNIQUE NOT NULL,  -- ÚNICO
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    puntos INT DEFAULT 0,  -- Sistema de puntos
    usuario_id INT,  -- Usuario que lo registró
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de artículos (CON CAMPO PROMOCIÓN)
CREATE TABLE IF NOT EXISTS articulos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    categoria VARCHAR(100),
    es_promocion BOOLEAN DEFAULT FALSE,  -- Si es artículo en promoción
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de ventas
CREATE TABLE IF NOT EXISTS ventas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT,
    cliente_nombre VARCHAR(200),
    total DECIMAL(10,2) NOT NULL,
    puntos_ganados INT DEFAULT 0,  -- Puntos ganados en esta venta
    fecha_venta DATE,
    usuario_id INT,
    estado ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'completada',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de detalle_ventas (CON CÓDIGO DE ARTÍCULO)
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    venta_id INT,
    articulo_id INT,
    articulo_codigo VARCHAR(50),  -- Código del artículo
    articulo_nombre VARCHAR(100),
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    es_promocion BOOLEAN DEFAULT FALSE,  -- Si fue canjeado por puntos
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES ventas(id),
    FOREIGN KEY (articulo_id) REFERENCES articulos(id)
);

-- Tabla de compras
CREATE TABLE IF NOT EXISTS compras (
    id INT PRIMARY KEY AUTO_INCREMENT,
    folio VARCHAR(50) NOT NULL UNIQUE,
    fecha DATE NOT NULL DEFAULT (CURRENT_DATE),
    estado ENUM('ACTIVA','CANCELADA') DEFAULT 'ACTIVA',
    articulo_id INT,
    articulo_nombre VARCHAR(100),
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_compra DATE,
    usuario_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (articulo_id) REFERENCES articulos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Insertar usuarios por defecto (CON RFC Y TELÉFONO)
INSERT INTO usuarios (username, password, nombre, apellido, email, telefono, rfc, rol) VALUES 
('admin', '123', 'Administrador', 'Sistema', 'admin@sistema.com', '3331234567', 'ADSI901010XXX', 'admin'),
('gerente', '123', 'Gerente', 'Principal', 'gerente@sistema.com', '3331234568', 'GEPR850520YYY', 'gerente'),
('cajero', '123', 'Cajero', 'Principal', 'cajero@sistema.com', '3331234569', 'CAPR920315ZZZ', 'cajero');

-- Insertar artículos de ejemplo (CON CATEGORÍAS Y PROMOCIONES)
INSERT INTO articulos (codigo, nombre, descripcion, precio, stock, categoria, es_promocion) VALUES 
('MED001', 'Paracetamol 500mg', 'Analgésico y antipirético', 8.50, 100, 'Medicamentos', FALSE),
('MED002', 'Ibuprofeno 400mg', 'Antiinflamatorio y analgésico', 12.75, 80, 'Medicamentos', FALSE),
('MED003', 'Amoxicilina 500mg', 'Antibiótico de amplio espectro', 25.00, 50, 'Medicamentos', FALSE),
('MED004', 'Omeprazol 20mg', 'Inhibidor de bomba de protones', 18.50, 60, 'Medicamentos', FALSE),
('MED005', 'Loratadina 10mg', 'Antihistamínico', 15.00, 70, 'Medicamentos', FALSE),
('CUI001', 'Jabón Antibacterial', 'Jabón líquido antibacterial', 15.50, 120, 'Cuidado Personal', FALSE),
('CUI002', 'Shampoo Anticaspa', 'Shampoo tratamiento anticaspa', 18.00, 90, 'Cuidado Personal', FALSE),
('CUI003', 'Pasta Dental', 'Pasta dental con flúor', 22.00, 150, 'Cuidado Personal', FALSE),
('SUP001', 'Vitamina C 1000mg', 'Suplemento vitamínico', 45.00, 40, 'Suplementos', FALSE),
('SUP002', 'Omega 3', 'Ácidos grasos esenciales', 120.00, 30, 'Suplementos', FALSE),
('SUP003', 'Multivitamínico', 'Complejo vitamínico', 85.00, 35, 'Suplementos', FALSE),
('HER001', 'Té Verde', 'Antioxidante natural', 35.00, 50, 'Herbolaria', FALSE),
('HER002', 'Manzanilla', 'Infusión relajante', 28.00, 60, 'Herbolaria', FALSE),
('PROM001', 'Gel Antibacterial 500ml', 'Promoción especial', 25.00, 200, 'Promociones', TRUE),
('PROM002', 'Kit Primeros Auxilios', 'Promoción 50 puntos', 50.00, 100, 'Promociones', TRUE);

-- Insertar clientes (CON RFC Y USUARIO_ID)
INSERT INTO clientes (rfc, nombre, apellido, email, telefono, direccion, puntos, usuario_id) VALUES 
('LOPC850315ABC', 'Carlos', 'López', 'carlos@email.com', '555-1234', 'Av. Salud 123', 0, 1),
('MARA900520XYZ', 'Ana', 'Martínez', 'ana@email.com', '555-5678', 'Calle Bienestar 456', 25, 1);
