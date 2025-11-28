from django.db import models
from django.utils import timezone


class ParametroSistema(models.Model):
    """Parametros tributarios versionados. HU16/HU19."""

    clave = models.CharField(max_length=120)
    valor = models.CharField(max_length=500)
    tipo = models.CharField(max_length=50, default='str')
    descripcion = models.TextField(null=True, blank=True)
    vigente_desde = models.DateField(default=timezone.now)
    vigente_hasta = models.DateField(null=True, blank=True)
    version = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'parametros_sistema'
        indexes = [
            models.Index(fields=['clave', 'version'], name='idx_param_clave_version'),
        ]

    def __str__(self) -> str:
        return f'{self.clave} v{self.version}'


class ReglaNegocio(models.Model):
    """Reglas de validacion HU18."""

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(null=True, blank=True)
    expresion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = 'reglas_negocio'

    def __str__(self) -> str:
        return self.nombre
