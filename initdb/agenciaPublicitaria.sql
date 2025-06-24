DROP DATABASE IF EXISTS campanias;
CREATE DATABASE campanias;

\c campanias

CREATE TABLE cliente(
    id SERIAL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    direccion_postal VARCHAR(100),
    numero_telefono VARCHAR(30),
    correo VARCHAR(100),
    CONSTRAINT pk_cliente PRIMARY KEY (id)
);

CREATE TABLE topicoPagina(
    id SERIAL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT pk_topico PRIMARY KEY (id)
);

CREATE TABLE categoria(
    id SERIAL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT pk_categoria PRIMARY KEY (id)
);

CREATE TABLE tipoAnuncio(
    id SERIAL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT pk_tipo PRIMARY KEY (id)
);

CREATE TABLE campania(
    id SERIAL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    CONSTRAINT pk_campania PRIMARY KEY (id)
);

CREATE TABLE paginaWeb(
    id SERIAL,
    url TEXT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    topico INTEGER,
    CONSTRAINT pk_paginaWeb PRIMARY KEY (id),
    CONSTRAINT fk_paginaWeb_topico FOREIGN KEY (topico) REFERENCES topicoPagina(id)
);

CREATE TABLE anuncio(
    codigo SERIAL,
    nombre VARCHAR(100) NOT NULL,
    tipo INTEGER,
    titulo VARCHAR(100) NOT NULL,
    contenido TEXT NOT NULL,
    categoria INTEGER,
    precio DECIMAL(10,2) CHECK (precio>0) NOT NULL,
    campania INTEGER NOT NULL,
    CONSTRAINT pk_anuncio PRIMARY KEY (codigo),
    CONSTRAINT fk_anuncio_tipoAnuncio FOREIGN KEY (tipo) REFERENCES tipoAnuncio(id),
    CONSTRAINT fk_anuncio_categoria FOREIGN KEY (categoria) REFERENCES categoria(id),
    CONSTRAINT fk_anuncio_campania FOREIGN KEY (campania) REFERENCES campania(id)
);

CREATE TABLE contratacionAnuncio(
    id SERIAL,
    fechaContratacion TIMESTAMP NOT NULL,
    cliente INTEGER NOT NULL,
    anuncio INTEGER NOT NULL,
    precio DECIMAL(10,2) CHECK (precio>0) NOT NULL,
    CONSTRAINT pk_contratacionAnuncio PRIMARY KEY (id),
    CONSTRAINT fk_contratacionAnuncio_cliente FOREIGN KEY (cliente) REFERENCES cliente(id),
    CONSTRAINT fk_contratacionAnuncio_anuncio FOREIGN KEY (anuncio) REFERENCES anuncio(codigo)
);

CREATE TABLE aparicionAnuncioPagina(
    id SERIAL,
    paginaWeb INTEGER NOT NULL,
    anuncio INTEGER NOT NULL,
    fechaInicioAparicion TIMESTAMP NOT NULL,
    fechaFinAparicion TIMESTAMP CHECK (fechaFinAparicion > fechaInicioAparicion),
    CONSTRAINT pk_aparicionAnuncioPagina PRIMARY KEY (id),
    CONSTRAINT fk_aparicionAnuncioPagina_anuncio FOREIGN KEY (anuncio) REFERENCES anuncio(codigo),
    CONSTRAINT fk_aparicionAnuncioPagina_pagina FOREIGN KEY (paginaWeb) REFERENCES paginaWeb(id)
);
