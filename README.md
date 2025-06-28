# Tutorial: Despliegue de una Aplicación Django con Docker y Postgres
Práctico de Mapeo Objeto-Relacional para la materia, Bases de Datos de la carrera `Ingeniería en Sistemas` de la *`Universidad Tecnológica Nacional`* *`Facultad Regional Villa María`*.

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Django 5.1.11](https://img.shields.io/badge/Django%205.1.11-092E20?style=for-the-badge&logo=django&logoColor=white)
![Alpine Linux](https://img.shields.io/badge/Alpine_Linux-0D597F?style=for-the-badge&logo=alpine-linux&logoColor=white)
![Python 3.13](https://img.shields.io/badge/Python%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL%2017-336791?style=for-the-badge&logo=postgresql&logoColor=white)

**Referencia Rápida**

**Mantenido Por:** Barrionuevo, Imanol; Broilo, Mateo Jose; Correa, Valentin; Díaz, Gabriel; Gambino, Tomás; Gomez Ferrero, Andres; Letona, Mateo; Wursten, Santiago

## **Descargo de Responsabilidad:**
El código proporcionado se ofrece "tal cual", sin garantía de ningún tipo, expresa o implícita. En ningún caso los autores o titulares de derechos de autor serán responsables de cualquier reclamo, daño u otra responsabilidad.

## Introducción
Este tutorial te guiará paso a paso en la creación y despliegue de una aplicación Django utilizando Docker y Docker Compose. El objetivo es que puedas levantar un entorno de desarrollo profesional, portable y fácil de mantener, ideal tanto para pruebas como para producción.

---

## Requisitos Previos
- **Docker** y **Docker Compose** instalados en tu sistema. Puedes consultar la [documentación oficial de Docker](https://docs.docker.com/get-docker/) para la instalación.
- Conocimientos básicos de Python y Django (no excluyente, el tutorial es autoexplicativo).

### Recursos Útiles
- [Tutorial oficial de Django](https://docs.djangoproject.com/en/2.0/intro/tutorial01/)
- [Cómo crear un entorno virtual en Python](https://docs.djangoproject.com/en/2.0/intro/contributing/)

---
## 1. Estructura del Proyecto
Crea una carpeta para tu proyecto. En este ejemplo, la llamaremos `agencia`.

> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal o archivo correspondiente.**
```sh
mkdir agencia
cd agencia/
```
---
2. Definición de Dependencias
Crea un archivo requirements.txt para listar las dependencias de Python necesarias para tu aplicación.

Puedes copiar todo este bloque y pegarlo directamente en tu archivo requirements.txt.

# requirements.txt
Django
psycopg[binary]  # Driver para PostgreSQL
---
## 3. Creación del Dockerfile
El `Dockerfile` define la imagen de Docker que contendrá tu aplicación. Aquí se detallan las etapas de construcción, instalación de dependencias y configuración del entorno.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo Dockerfile.**
```dockerfile
# Etapa de construcción
FROM python:3.13-alpine AS base
LABEL maintainer="Santiago Wursten Gill <santiwgwuri@gmail.com>, Imanol Barrionuevo <barrionuevoimanol@gmail.com>"
LABEL version="1.0"
LABEL description="cloudset"
RUN apk --no-cache add bash pango ttf-freefont py3-pip curl

# Etapa de construcción
FROM base AS builder
# Instalación de dependencias de construcción
RUN apk --no-cache add py3-pip py3-pillow py3-brotli py3-scipy py3-cffi \
  linux-headers autoconf automake libtool gcc cmake python3-dev \
  fortify-headers binutils libffi-dev wget openssl-dev libc-dev \
  g++ make musl-dev pkgconf libpng-dev openblas-dev build-base \
  font-noto terminus-font libffi

# Copia solo los archivos necesarios para instalar dependencias de Python
COPY ./requirements.txt .

# Instalación de dependencias de Python
RUN pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt \
  && rm requirements.txt

# Etapa de producción
FROM base
RUN mkdir /code
WORKDIR /code
# Copia solo los archivos necesarios desde la etapa de construcción
COPY ./requirements.txt .
RUN pip install -r requirements.txt \
  && rm requirements.txt
COPY --chown=user:group --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.12/site-packages 
#COPY --from=build-python /usr/local/bin/ /usr/local/bin/
ENV PATH /usr/local/lib/python3.13/site-packages:$PATH
# Configuración adicional
RUN ln -s /usr/share/zoneinfo/America/Cordoba /etc/localtime

# Comando predeterminado
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "app.wsgi"]

```

---
## 4. Configuración de Variables de Entorno
Crea un archivo `.env.db` para almacenar las variables de entorno necesarias para la conexión a la base de datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo .env.db.**
```conf
# .env.db
# .env.db
DATABASE_ENGINE=django.db.backends.postgresql
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
PGUSER=${POSTGRES_USER}
POSTGRES_PASSWORD=postgres
LANG=es_AR.utf8
POSTGRES_INITDB_ARGS="--locale-provider=icu --icu-locale=es-AR --auth-local=trust"
```

---
