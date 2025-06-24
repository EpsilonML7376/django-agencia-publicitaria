from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class NombreAbstract(models.Model):
    nombre = models.CharField(
        _('Nombre'),
        help_text=_('Nombre descriptivo'),
        max_length=200,
        # unique=True,
    )

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.nombre}'

    class Meta:
        abstract = True
        ordering = ['nombre']


class Localidad(NombreAbstract):
    class Meta:
        verbose_name = 'localidad'
        verbose_name_plural = 'localidades'


class Barrio(NombreAbstract):
    class Meta:
        verbose_name = 'barrio'
        verbose_name_plural = 'barrios'


class Provincia(NombreAbstract):
    class Meta:
        verbose_name = 'provincia'
        verbose_name_plural = 'provincias'


class Producto(NombreAbstract):
    ganancia = models.DecimalField(
        _('Ganancia'),
        max_digits=15,
        decimal_places=2,
        help_text=_('Ganancia del producto, expresado en coeficiente.'),
        default=0
    )
    es_relleno = models.BooleanField(
        _('Es Relleno'),
        help_text=_('Especifica si el producto contiene relleno.'),
        default=False
    )

    @property
    def precio(self):
        total = 0
        for ingrediente in self.ingredientes.all():
            total += ingrediente.cantidad * ingrediente.ingrediente.costo
        return round(total * self.ganancia, 2)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'


class Cliente(NombreAbstract):
    numero_documento = models.BigIntegerField(
        _('numero documento'),
        help_text=_('numero de documento / CUIT'),
        null=True
    )
    direccion = models.CharField(
        _('dirección'),
        help_text=_('dirección del cliente'),
        max_length=200,
        blank=True,
        null=True
    )
    celular = models.BigIntegerField(
        _('Celular'),
        help_text=_(
            'Número de celular con característica del/la administrador/a'),
        blank=True,
        null=True
    )
    telefono = models.BigIntegerField(
        _('teléfono'),
        help_text=_('teléfono fijo'),
        blank=True,
        null=True
    )
    email = models.EmailField(
        _('email'),
        help_text=_('email del cliente'),
        null=True,
        blank=True,
    )
    barrio = models.ForeignKey(
        Barrio,
        verbose_name=_('barrio'),
        help_text=_('barrio donde reside '),
        related_name='%(app_label)s_%(class)s_related',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    localidad = models.ForeignKey(
        Localidad,
        verbose_name=_('localidad'),
        help_text=_('localidad donde reside el cliente'),
        related_name='%(app_label)s_%(class)s_related',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    provincia = models.ForeignKey(
        Provincia,
        verbose_name=_('provincia'),
        help_text=_('provincia donde reside'),
        related_name='%(app_label)s_%(class)s_related',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        User,
        help_text=_('Usuario con el que se loguea al sistema'),
        verbose_name='usuario',
        related_name='%(app_label)s_%(class)s',
        related_query_name='%(app_label)s_%(class)s',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return '{} {}'.format(self.nombre, self.numero_documento)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    'numero_documento',
                    'user',
                ],
                name='%(app_label)s_%(class)s_unico'
            ),
        ]


class Venta(models.Model):
    fecha = models.DateField(
        _('fecha'),
        help_text=_('fecha de la venta')
    )
    cliente = models.ForeignKey(
        Cliente,
        verbose_name=_('cliente'),
        help_text=_('cliente que realiza la compra'),
        related_name='compras',
        on_delete=models.PROTECT,
        blank=False,
        null=False
    )

    def __str__(self):
        return '{} {}'.format(self.fecha, self.cliente.nombre)

    class Meta:
        ordering = ['fecha']
        verbose_name = 'venta'
        verbose_name_plural = 'ventas'


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        verbose_name=_('venta'),
        help_text=_('detalle de la compra'),
        related_name='detalle',
        on_delete=models.PROTECT,
        blank=False,
        null=False
    )
    cantidad = models.DecimalField(
        _('cantidad'),
        max_digits=15,
        decimal_places=2,
        help_text=_('cantidad'),
        blank=True,
        null=True,
        default=None
    )
    producto = models.ForeignKey(
        Producto,
        verbose_name=_('producto'),
        help_text=_('producto'),
        related_name='detalle',
        on_delete=models.PROTECT,
        blank=False,
        null=False
    )


class UnidadMedida(NombreAbstract):
    pass


class Ingrediente(NombreAbstract):
    costo = models.DecimalField(
        _('Costo'),
        max_digits=15,
        decimal_places=2,
        help_text=_('Costo del ingrediente expresado en pesos'),
        default=0
    )
    unidad_medida = models.ForeignKey(
        UnidadMedida,
        related_name='ingredientes',
        on_delete=models.PROTECT,
        help_text=_('Unidad de medida del ingrediente'),
        null=False,
        blank=False,
        default=1
    )

    class Meta:
        verbose_name = _('Ingrediente')
        verbose_name_plural = _('Ingredientes')


class Receta(models.Model):
    cantidad = models.DecimalField(
        _('Cantidad'),
        max_digits=15,
        decimal_places=3,
        help_text=_(
            'Cantidad del ingrediente, expresado en su unidad de medida.'),
        default=0
    )
    ingrediente = models.ForeignKey(
        Ingrediente,
        related_name='productos',
        on_delete=models.PROTECT,
        help_text=_('Ingrediente de la receta'),
    )
    producto = models.ForeignKey(
        Producto,
        related_name='ingredientes',
        on_delete=models.PROTECT,
        help_text=_('Producto de la receta'),
    )

    class Meta:
        ordering = ['ingrediente']
        verbose_name = _('Producto')
        verbose_name_plural = _('Productos')
