from django.db import models
from django.utils import timezone
from .usuarios import Usuario


class Documento(models.Model):
    """Gestión documental básica alineada a tabla documentos del esquema actual."""

    id_documento = models.AutoField(primary_key=True, db_column='id_documento')
    tipo_documento = models.CharField(max_length=50, db_column='tipo_documento')
    id_emisor = models.IntegerField(null=True, blank=True, db_column='id_emisor')
    id_instrumento = models.IntegerField(null=True, blank=True, db_column='id_instrumento')
    ruta_archivo = models.TextField(db_column='ruta_archivo')
    version = models.IntegerField(default=1)
    visibilidad = models.CharField(max_length=50, default='empleados')
    fecha_creacion = models.DateTimeField(default=timezone.now, db_column='fecha_creacion')
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='creado_por',
        related_name='documentos_creados',
    )
    aprobado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='aprobado_por',
        related_name='documentos_aprobados',
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, db_column='fecha_aprobacion')

    class Meta:
        managed = False
        db_table = 'documentos'

    def __str__(self) -> str:
        return self.ruta_archivo

    @property
    def filename(self):
        return self.ruta_archivo


class ArchivoCarga(models.Model):
    """Carga masiva (HU04/HU12) marcada como futura: solo tracking."""

    class Estado(models.TextChoices):
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        COMPLETADA = 'COMPLETADA', 'Completada'
        FALLIDA = 'FALLIDA', 'Fallida'

    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='cargas')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.EN_PROCESO)
    total_registros = models.IntegerField(null=True, blank=True)
    procesados_ok = models.IntegerField(null=True, blank=True)
    procesados_err = models.IntegerField(null=True, blank=True)
    errores = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cargas_creadas',
    )

    class Meta:
        managed = False
        db_table = 'archivo_carga'
        indexes = [
            models.Index(fields=['estado'], name='idx_carga_estado'),
            models.Index(fields=['created_at'], name='idx_carga_created_at'),
        ]

    def __str__(self) -> str:
        return f'Carga #{self.pk}'


class ArchivoCargaDetalle(models.Model):
    """Detalle de carga masiva (placeholder futuro)."""

    class Estado(models.TextChoices):
        OK = 'OK', 'Correcto'
        ERROR = 'ERROR', 'Error'
        ADVERTENCIA = 'ADVERTENCIA', 'Advertencia'

    archivo_carga = models.ForeignKey(ArchivoCarga, on_delete=models.CASCADE, related_name='detalles')
    fila_numero = models.IntegerField()
    datos = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ERROR)
    errores = models.TextField(null=True, blank=True)
    calificacion = models.ForeignKey(
        'appNuam.Calificacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalles_carga',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'archivo_carga_detalle'
        indexes = [
            models.Index(fields=['archivo_carga', 'fila_numero'], name='idx_carga_det_fila'),
            models.Index(fields=['estado'], name='idx_carga_det_estado'),
        ]

    def __str__(self) -> str:
        return f'Detalle #{self.pk}'


class InformeOficial(models.Model):
    """Informes descargables (HU17)."""

    calificacion = models.ForeignKey('appNuam.Calificacion', on_delete=models.CASCADE, related_name='informes')
    documento = models.ForeignKey(Documento, to_field='id_documento', db_column='documento_id', on_delete=models.CASCADE, related_name='informes')
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='informes_creados',
    )

    class Meta:
        managed = False
        db_table = 'informes_oficiales'

    def __str__(self) -> str:
        return self.descripcion or f'Informe #{self.pk}'
