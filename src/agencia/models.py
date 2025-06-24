from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class NombreAbstract(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=100,
    )

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.nombre}'

    class Meta:
        abstract = True
        ordering = ['nombre']

class TopicoPagina(NombreAbstract):
    class Meta:
        verbose_name = _('Tópico de Página')
        verbose_name_plural = _('Tópicos de Páginas')


class Categoria(NombreAbstract):
    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')


class TipoAnuncio(NombreAbstract):
    class Meta:
        verbose_name = _('Tipo de Anuncio')
        verbose_name_plural = _('Tipos de Anuncios')


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
        blank=True,
        null=True
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
    categoria = models.ForeignKey(
        Categoria,
        verbose_name=_('Categoría'),
        help_text=_('Categoría del anuncio'),
        related_name='anuncios',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
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

class AparicionAnuncioPagina(models.Model):
    anuncio = models.ForeignKey(
        Anuncio,
        verbose_name=_('Anuncio'),
        help_text=_('Anuncio que aparece en la página'),
        related_name='apariciones',
        on_delete=models.PROTECT
    )
    fechaInicioAparicion = models.DateTimeField(
        _('Fecha de Inicio'),
        help_text=_('Fecha y hora de inicio de aparición')
    )
    fechaFinAparicion = models.DateTimeField(
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
        blank=True,
        null=True
    )

    apariciones = models.ForeignKey(
        AparicionAnuncioPagina,
        verbose_name=_('Aparición'),
        help_text=_('Aparición de un anuncio en página'),
        related_name='apariciones',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _('Página Web')
        verbose_name_plural = _('Páginas Web')
        ordering = ['nombre']

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
    direccionPostal = models.CharField(
        _('Dirección Postal'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Dirección postal del cliente')
    )
    numeroTelefono = models.CharField(
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

    contrataciones = models.ForeignKey(
        ContratacionAnuncio,
        verbose_name=_('Contratación de anuncio'),
        help_text=_('Contrataciones de un anuncio'),
        related_name='contrataciones',
        on_delete=models.PROTECT
    )

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['apellido', 'nombre']

class Campania(models.Model):
    class Meta:
        verbose_name = _('Campaña')
        verbose_name_plural = _('Campañas')

    nombre = models.CharField(
        _('Nombre'),
        max_length=50,
        help_text=_('Nombre de la campaña')
    )
    
    anuncio = models.ForeignKey(
        Anuncio,
        verbose_name=_('Anuncio'),
        help_text=_('Anuncio que pertenece a la campaña'),
        related_name='campañas',
        on_delete=models.PROTECT
    )

    fechaInicio = models.DateTimeField(
        _('Fecha de Inicio'),
        help_text=_('Fecha y hora de inicio de campaña')
    )
    fechaFin = models.DateTimeField(
        _('Fecha de Fin'),
        help_text=_('Fecha y hora de fin de campaña'),
        blank=True,
        null=True
    )
