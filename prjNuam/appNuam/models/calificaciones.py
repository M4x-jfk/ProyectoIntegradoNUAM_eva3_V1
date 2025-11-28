from decimal import Decimal
from django.db import models
from django.utils import timezone
from .usuarios import Usuario


class Emisor(models.Model):
    """Emisor alineado a tabla emisores."""

    id_emisor = models.AutoField(primary_key=True, db_column='id_emisor')
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, null=True, blank=True)
    tipo_emisor = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=20, default='activo')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'emisores'

    def __str__(self) -> str:
        return self.nombre


class Instrumento(models.Model):
    """Instrumento alineado a tabla instrumentos."""

    id_instrumento = models.AutoField(primary_key=True, db_column='id_instrumento')
    emisor = models.ForeignKey(Emisor, on_delete=models.CASCADE, db_column='id_emisor', related_name='instrumentos')
    codigo_interno = models.CharField(max_length=50, null=True, blank=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    tipo_instrumento = models.CharField(max_length=50, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='activo')

    class Meta:
        managed = False
        db_table = 'instrumentos'

    def __str__(self) -> str:
        return self.nombre or f'Instrumento #{self.id_instrumento}'


class Calificacion(models.Model):
    """Calificaciones tributarias alineadas a calificaciones_tributarias."""

    class EstadoRegistro(models.TextChoices):
        VIGENTE = 'vigente', 'Vigente'
        REEMPLAZADO = 'reemplazado', 'Reemplazado'
        ANULADO = 'anulado', 'Anulado'

    class Origen(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        CARGA_MASIVA = 'carga_masiva', 'Carga masiva'
        IA = 'ia', 'IA'

    id_calificacion = models.AutoField(primary_key=True, db_column='id_calificacion')
    emisor = models.ForeignKey(Emisor, on_delete=models.CASCADE, db_column='id_emisor', related_name='calificaciones')
    instrumento = models.ForeignKey(
        Instrumento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_instrumento',
        related_name='calificaciones',
    )
    anio = models.IntegerField()
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    factor = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)
    rating = models.CharField(max_length=20, null=True, blank=True)
    estado_registro = models.CharField(max_length=20, choices=EstadoRegistro.choices, default=EstadoRegistro.VIGENTE)
    origen = models.CharField(max_length=20, choices=Origen.choices, default=Origen.MANUAL)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='creado_por',
        related_name='calificaciones_creadas',
    )
    fecha_creacion = models.DateTimeField(default=timezone.now, db_column='fecha_creacion')
    modificado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='modificado_por',
        related_name='calificaciones_modificadas',
    )
    fecha_modificacion = models.DateTimeField(null=True, blank=True, db_column='fecha_modificacion')

    class Meta:
        managed = False
        db_table = 'calificaciones_tributarias'
        indexes = [
            models.Index(fields=['emisor', 'anio'], name='idx_calif_emisor_anio'),
            models.Index(fields=['estado_registro'], name='idx_calif_estado_reg'),
            models.Index(fields=['origen'], name='idx_calif_origen'),
        ]

    def __str__(self) -> str:
        return f'Calificación #{self.id_calificacion}'

    def soft_delete(self, user: Usuario | None = None):
        self.estado_registro = self.EstadoRegistro.ANULADO
        self.modificado_por = user
        self.fecha_modificacion = timezone.now()
        self.save(update_fields=['estado_registro', 'modificado_por', 'fecha_modificacion'])


class CalificacionHistorial(models.Model):
    """Historial detallado por calificacion. HU06."""

    class Accion(models.TextChoices):
        CREAR = 'CREAR', 'Crear'
        MODIFICAR = 'MODIFICAR', 'Modificar'
        ELIMINAR = 'ELIMINAR', 'Eliminar'
        ANULAR = 'ANULAR', 'Anular'
        RESTAURAR = 'RESTAURAR', 'Restaurar'
        APROBAR = 'APROBAR', 'Aprobar'
        RECHAZAR = 'RECHAZAR', 'Rechazar'

    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='acciones')
    accion = models.CharField(max_length=15, choices=Accion.choices)
    detalle = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'historial_accion'

    def __str__(self) -> str:
        return f'{self.get_accion_display()} por {self.usuario}'


class Aprobacion(models.Model):
    """Flujo basico de aprobacion HU14."""

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'

    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, related_name='aprobaciones')
    aprobador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='aprobaciones')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    motivo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'aprobaciones'
        indexes = [
            models.Index(fields=['estado'], name='idx_aprobacion_estado'),
            models.Index(fields=['calificacion'], name='idx_aprobacion_calif'),
        ]

    def __str__(self) -> str:
        return f'Aprobacion {self.estado} #{self.pk}'


def calcular_factor_base(monto: Decimal, coef: Decimal = Decimal('0.05')) -> Decimal:
    """Helper usada por services; mantiene compatibilidad si no hay params en BD."""
    return (monto or Decimal('0')) * coef
