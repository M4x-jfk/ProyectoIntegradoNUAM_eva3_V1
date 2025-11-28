from django.db import models
from django.utils import timezone
from .usuarios import Usuario
from .documentos import Documento


class AuditoriaEvento(models.Model):
    """Auditoria global HU10/HU20."""

    actor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')
    accion = models.CharField(max_length=120)
    objeto = models.CharField(max_length=120, null=True, blank=True)
    objeto_id = models.CharField(max_length=64, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'auditoria_eventos'
        indexes = [
            models.Index(fields=['accion', 'created_at'], name='idx_evento_accion_fecha'),
        ]

    def __str__(self) -> str:
        return f'{self.accion} - {self.created_at}'


class Reporte(models.Model):
    """Registro de reportes/exportaciones. HU05/HU17."""

    class Tipo(models.TextChoices):
        CERTIFICADO_TRIBUTARIO = 'CERTIFICADO_TRIBUTARIO', 'Certificado tributario'
        REPORTE_AUDITORIA = 'REPORTE_AUDITORIA', 'Reporte auditoria'
        EXPORTACION = 'EXPORTACION', 'Exportacion'
        BACKUP = 'BACKUP', 'Backup'

    class Formato(models.TextChoices):
        PDF = 'PDF', 'PDF'
        CSV = 'CSV', 'CSV'
        XLSX = 'XLSX', 'XLSX'
        JSON = 'JSON', 'JSON'
        ZIP = 'ZIP', 'ZIP'

    tipo = models.CharField(max_length=40, choices=Tipo.choices)
    formato = models.CharField(max_length=4, choices=Formato.choices, default=Formato.PDF)
    documento = models.ForeignKey(Documento, to_field='id_documento', db_column='documento_id', on_delete=models.CASCADE, related_name='reportes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes')
    party = models.ForeignKey('appNuam.Emisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes')
    calificacion = models.ForeignKey(
        'appNuam.Calificacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes',
    )
    parametros = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'reportes'
        indexes = [
            models.Index(fields=['tipo', 'created_at'], name='idx_reportes_tipo_fecha'),
        ]

    def __str__(self) -> str:
        return f'Reporte {self.get_tipo_display()}'


class HistorialAccion(models.Model):
    """Alias de historial global (compat). HU06/HU10."""

    class Accion(models.TextChoices):
        CREAR = 'CREAR', 'Crear'
        MODIFICAR = 'MODIFICAR', 'Modificar'
        ELIMINAR = 'ELIMINAR', 'Eliminar'
        ANULAR = 'ANULAR', 'Anular'
        RESTAURAR = 'RESTARURAR', 'Restaurar'

    calificacion = models.ForeignKey('appNuam.Calificacion', on_delete=models.CASCADE, related_name='historial_legacy')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='acciones_legacy')
    accion = models.CharField(max_length=15, choices=Accion.choices)
    detalle = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'historial_accion'

    def __str__(self) -> str:
        return f'{self.get_accion_display()} por {self.usuario}'


class BackupEstado(models.Model):
    """Estado de backups. HU20."""

    ultimo_backup = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=40, default='DESCONOCIDO')
    mensaje = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'backup_estado'

    def __str__(self) -> str:
        return f'Backup {self.estado}'
