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
## 2. Definición de Dependencias
Crea un archivo requirements.txt para listar las dependencias de Python necesarias para tu aplicación.

Puedes copiar todo este bloque y pegarlo directamente en tu archivo requirements.txt.
```txt
# requirements.txt
Django
psycopg[binary]  # Driver para PostgreSQL
```
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
## 5. Definición de Servicios con Docker Compose
El archivo `docker-compose.yml` orquesta los servicios necesarios: base de datos, backend de Django y utilidades para generación y administración del proyecto.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo docker-compose.yml.**
```yml
services:
  db:
    image: postgres:alpine
    env_file:
      - .env.db
    environment:
      - POSTGRES_INITDB_ARGS=--auth-host=md5 --auth-local=trust
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready" ]
      interval: 10s
      timeout: 2s
      retries: 5
    volumes:
      - postgres-db:/var/lib/postgresql/data
    ports:
      - 6432:5432
    networks:
      - net

  backend:
    build: .
    command: runserver 0.0.0.0:8000
    entrypoint: python3 manage.py
    env_file:
      - .env.db
    expose:
      - "8000"
    ports:
      - "8000:8000"
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

  generate:
    build: .
    user: root
    command: /bin/sh -c 'mkdir src && django-admin startproject app src'
    env_file:
      - .env.db
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/code
    networks:
      - net

  manage:
    build: .
    entrypoint: python3 manage.py
    env_file:
      - .env.db
    volumes:
      - ./src:/code
    depends_on:
      db:
        condition: service_healthy
    networks:
      - net

networks:
  net:

volumes:
  postgres-db:
```

---
## 6. Generación y Configuración de la Aplicación

### Generar la estructura base del proyecto y la app

Hay que tener el archivo `LICENSE` para que la generación de a imagen no produzca un error.
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm generate
docker compose run --rm manage startapp agencia
sudo chown $USER:$USER -R .
```

### Configuración de `settings.py`
Edita el archivo `settings.py` para agregar tu app y configurar la base de datos usando las variables de entorno.

> **Puedes copiar todo este bloque y pegarlo al final directamente en tu archivo ./src/app/settings.py.**
```python
import os
ALLOWED_HOSTS = [os.environ.get("ALLOWED_HOSTS", "*")]
INSTALLED_APPS += [
    'agencia',  # Agrega tu app aquí
]
# Configuración de la base de datos
DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "") or os.getenv("DB_NAME")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "") or os.getenv("DB_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "") or os.getenv("DB_PORT")
DATABASES = {
    "default": {
        "ENGINE": DATABASE_ENGINE,
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
    }
}
```

---
## 7. Primeros Pasos con Django

### Migrar la base de datos
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage migrate
```

### Crear un superusuario
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose run --rm manage createsuperuser
```

### Iniciar la aplicación
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose up -d backend
```
Accede a la administración de Django en [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Ver logs de los contenedores
> **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
```sh
docker compose logs -f
```

---
## 8. Comandos Útiles
- **Aplicar migraciones:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose run manage makemigrations
  docker compose run manage migrate
  ```
- **Detener y eliminar contenedores:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose down
  ```
- **Detener y eliminar contenedores con imagenes y contenedores sin uso:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker compose down -v --remove-orphans --rmi all
  ```
- **Limpiar recursos de Docker:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  docker system prune -a
  ```
- **Cambiar permisos de archivos:**
  > **Puedes copiar todo este bloque y pegarlo directamente en tu terminal.**
  ```sh
  sudo chown $USER:$USER -R .
  ```

---
## 9. Modelado de la Aplicación

### Ejemplo de `models.py`
Incluye modelos bien documentados y estructurados para una gestión profesional de tus datos.

> **Puedes copiar todo este bloque y pegarlo directamente en tu archivo ./src/pastas/models.py.**
```python
from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class TopicoPagina(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=50,
        unique=True
    )
    descripcion= models.CharField(
        _('Descripción'),
        help_text=_('Descripción del tópico de página'),
        max_length=150,
        blank=True,
        null=True
    )
    def __str__(self) -> str:
        return f'{self.nombre}'

    class Meta:
        ordering = ['nombre']
        verbose_name = _('Tópico de Página')
        verbose_name_plural = _('Tópicos de Páginas')


class Categoria(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=50,
        unique=True
    )
    descripcion= models.CharField(
        _('Descripción'),
        help_text=_('Descripción de la categoría de anuncios'),
        max_length=150,
        blank=True,
        null=True
    )
    def __str__(self):
        return f'{self.nombre}'

    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')
        ordering = ['nombre']


class TipoAnuncio(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=50,
        unique=True
    )
    descripcion= models.CharField(
        _('Descripción'),
        help_text=_('Descripción del tipo de anuncios'),
        max_length=150,
        blank=True,
        null=True
    )
    def __str__(self):
        return f'{self.nombre}'

    class Meta:
        verbose_name = _('Tipo de Anuncio')
        verbose_name_plural = _('Tipos de Anuncios')
        ordering = ['nombre']

class Campania(models.Model):

    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre de la campaña'),
        unique=True
    )
    

    fecha_inicio = models.DateTimeField(
        _('Fecha de Inicio'),
        help_text=_('Fecha y hora de inicio de campaña')
    )
    fecha_fin = models.DateTimeField(
        _('Fecha de Fin'),
        help_text=_('Fecha y hora de fin de campaña'),
        blank=True,
        null=True
    )
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = _('Campaña')
        verbose_name_plural = _('Campañas')
        ordering=['nombre']
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(_('La fecha de fin debe ser posterior a la fecha de inicio'))


class Anuncio(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=100,
        help_text=_('Nombre del anuncio')
    )
    tipo = models.ForeignKey(
        TipoAnuncio,
        verbose_name=_('Tipo'),
        help_text=_('Tipo de anuncio'),
        related_name='anuncios',
        on_delete=models.SET_NULL,
    )
    titulo = models.CharField(
        _('Título'),
        max_length=100,
        help_text=_('Título del anuncio')
    )
    contenido = models.TextField(
        _('Contenido'),
        help_text=_('Contenido del anuncio')
    )
    campania=models.ForeignKey(
        Campania,
        verbose_name=_('Campaña'),
        help_text=_('Campaña donde aparece el anuncio'),
        related_name='anuncios',
        on_delete=models.PROTECT
    )
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('Categoría'),
        help_text=_('Categoría del anuncio'),
        related_name='anuncios',
        on_delete=models.SET_NULL,
    )
    precio = models.DecimalField(
        _('Precio'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Precio del anuncio')
    )

    def __str__(self):
        return f'{self.nombre} - {self.titulo}'

    class Meta:
        verbose_name = _('Anuncio')
        verbose_name_plural = _('Anuncios')
        ordering = ['nombre']

class PaginaWeb(models.Model):
    url = models.URLField(
        _('URL'),
        help_text=_('URL de la página web')
    )
    nombre = models.CharField(
        _('Nombre'),
        max_length=100,
        help_text=_('Nombre de la página web')
    )
    topico = models.ForeignKey(
        TopicoPagina,
        verbose_name=_('Tópico'),
        help_text=_('Tópico de la página web'),
        related_name='paginas',
        on_delete=models.SET_NULL,
    )
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _('Página Web')
        verbose_name_plural = _('Páginas Web')
        ordering = ['nombre']

class AparicionAnuncioPagina(models.Model):
    anuncio = models.ForeignKey(
        Anuncio,
        verbose_name=_('Anuncio'),
        help_text=_('Anuncio que aparece en la página'),
        related_name='apariciones',
        on_delete=models.PROTECT
    )
    pagina_web=models.ForeignKey(
        PaginaWeb,
        verbose_name='Página Web',
        help_text='Página web',
        related_name='apariciones',
        on_delete=models.PROTECT
    )
    fecha_inicio_aparicion = models.DateTimeField(
        _('Fecha de Inicio'),
        help_text=_('Fecha y hora de inicio de aparición')
    )
    fecha_fin_aparicion = models.DateTimeField(
        _('Fecha de Fin'),
        help_text=_('Fecha y hora de fin de aparición'),
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.anuncio.nombre} en {self.pagina_web.nombre}'

    class Meta:
        verbose_name = _('Aparición de Anuncio en Página')
        verbose_name_plural = _('Apariciones de Anuncios en Páginas')
        ordering = ['-fecha_inicio_aparicion']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_fin_aparicion and self.fecha_fin_aparicion <= self.fecha_inicio_aparicion:
            raise ValidationError(_('La fecha de fin debe ser posterior a la fecha de inicio'))

class Cliente(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre del cliente')
    )
    apellido = models.CharField(
        _('Apellido'),
        max_length=50,
        help_text=_('Apellido del cliente')
    )
    direccion_postal = models.CharField(
        _('Dirección Postal'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Dirección postal del cliente')
    )
    numero_telefono = models.CharField(
        _('Número de Teléfono'),
        max_length=30,
        blank=True,
        null=True,
        help_text=_('Número de teléfono del cliente')
    )
    correo = models.EmailField(
        _('Correo Electrónico'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Correo electrónico del cliente')
    )

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['apellido', 'nombre']


class ContratacionAnuncio(models.Model):
    fecha_contratacion = models.DateTimeField(
        _('Fecha de Contratación'),
        help_text=_('Fecha y hora de contratación del anuncio')
    )
    anuncio = models.ForeignKey(
        Anuncio,
        verbose_name=_('Anuncio'),
        help_text=_('Anuncio contratado'),
        related_name='contrataciones',
        on_delete=models.PROTECT
    )
    cliente= models.ForeignKey(
        Cliente,
        verbose_name=_('Cliente'),
        help_text=_('Cliente que contrata el anuncio'),
        related_name='contrataciones',
        on_delete=models.PROTECT
    )
    precio = models.DecimalField(
        _('Precio'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Precio de la contratación')
    )

    def __str__(self):
        return f'{self.cliente} - {self.anuncio.nombre} ({self.fecha_contratacion})'

    class Meta:
        verbose_name = _('Contratación de Anuncio')
        verbose_name_plural = _('Contrataciones de Anuncios')
        ordering = ['-fecha_contratacion']

```

---
