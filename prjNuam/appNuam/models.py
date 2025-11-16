from django.db import models
from django.utils import timezone


class Rol(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self) -> str:
        return self.nombre


class Usuario(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        BLOQUEADO = 'BLOQUEADO', 'Bloqueado'
        SUSPENDIDO = 'SUSPENDIDO', 'Suspendido'

    nombre = models.CharField(max_length=120, null=True, blank=True)
    correo = models.EmailField(max_length=180, unique=True)
    hash_password = models.CharField(max_length=255)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.ACTIVO)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    roles = models.ManyToManyField('Rol', through='UsuarioRol', related_name='usuarios')

    class Meta:
        db_table = 'usuarios'
        indexes = [
            models.Index(fields=['correo'], name='idx_usuarios_correo'),
        ]

    def __str__(self) -> str:
        return self.correo


class UsuarioRol(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='rel_roles')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='rel_usuarios')

    class Meta:
        db_table = 'usuario_roles'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'rol'], name='uniq_usuario_rol'),
        ]

    def __str__(self) -> str:
        return f'{self.usuario} · {self.rol}'


class Documento(models.Model):
    class Formato(models.TextChoices):
        PDF = 'PDF', 'PDF'
        CSV = 'CSV', 'CSV'
        XLSX = 'XLSX', 'XLSX'
        JSON = 'JSON', 'JSON'
        ZIP = 'ZIP', 'ZIP'

    filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=120, null=True, blank=True)
    formato = models.CharField(max_length=4, choices=Formato.choices, null=True, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    checksum_sha256 = models.CharField(max_length=100, null=True, blank=True)
    storage_uri = models.CharField(max_length=500, null=True, blank=True)
    version = models.IntegerField(default=1)
    metadata = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_creados',
    )

    class Meta:
        db_table = 'documentos'

    def __str__(self) -> str:
        return self.filename


class Party(models.Model):
    class Tipo(models.TextChoices):
        PERSONA_NATURAL = 'PERSONA_NATURAL', 'Persona natural'
        PERSONA_JURIDICA = 'PERSONA_JURIDICA', 'Persona jurídica'

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    rut = models.CharField(max_length=20, null=True, blank=True)
    nombre_legal = models.CharField(max_length=200)
    nick_name = models.CharField(max_length=200, null=True, blank=True)
    email_contacto = models.EmailField(max_length=180, null=True, blank=True)
    telefono = models.CharField(max_length=40, null=True, blank=True)
    direccion = models.CharField(max_length=240, null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partys_creados',
    )
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partys_actualizados',
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partys_eliminados',
    )

    class Meta:
        db_table = 'party'
        indexes = [
            models.Index(fields=['rut'], name='idx_party_rut'),
            models.Index(fields=['tipo'], name='idx_party_tipo'),
        ]
        verbose_name = 'Party'
        verbose_name_plural = 'Partys'

    def __str__(self) -> str:
        return self.nombre_legal


class ArchivoCarga(models.Model):
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
        db_table = 'archivo_carga'
        indexes = [
            models.Index(fields=['estado'], name='idx_carga_estado'),
            models.Index(fields=['created_at'], name='idx_carga_created_at'),
        ]

    def __str__(self) -> str:
        return f'Carga #{self.pk}'


class Calificacion(models.Model):
    class Estado(models.TextChoices):
        VIGENTE = 'VIGENTE', 'Vigente'
        ANULADA = 'ANULADA', 'Anulada'
        PENDIENTE_APROBACION = 'PENDIENTE_APROBACION', 'Pendiente aprobación'
        RECHAZADA = 'RECHAZADA', 'Rechazada'

    class Fuente(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual'
        CARGA_MASIVA = 'CARGA_MASIVA', 'Carga masiva'
        API = 'API', 'API'

    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='calificaciones')
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    factor = models.DecimalField(max_digits=10, decimal_places=6)
    fecha = models.DateField()
    estado = models.CharField(max_length=24, choices=Estado.choices, default=Estado.VIGENTE)
    fuente = models.CharField(max_length=20, choices=Fuente.choices, default=Fuente.MANUAL)
    archivo_carga = models.ForeignKey(
        ArchivoCarga,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones',
    )
    observaciones = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones_creadas',
    )
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones_actualizadas',
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones_eliminadas',
    )

    class Meta:
        db_table = 'calificaciones'
        indexes = [
            models.Index(fields=['party', 'fecha'], name='idx_calif_party_fecha'),
            models.Index(fields=['estado'], name='idx_calif_estado'),
            models.Index(fields=['fuente'], name='idx_calif_fuente'),
        ]

    def __str__(self) -> str:
        return f'Calificación #{self.pk}'


class ArchivoCargaDetalle(models.Model):
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
        Calificacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detalles_carga',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'archivo_carga_detalle'
        indexes = [
            models.Index(fields=['archivo_carga', 'fila_numero'], name='idx_carga_det_fila'),
            models.Index(fields=['estado'], name='idx_carga_det_estado'),
        ]

    def __str__(self) -> str:
        return f'Detalle #{self.pk}'


class HistorialAccion(models.Model):
    class Accion(models.TextChoices):
        CREAR = 'CREAR', 'Crear'
        MODIFICAR = 'MODIFICAR', 'Modificar'
        ELIMINAR = 'ELIMINAR', 'Eliminar'
        ANULAR = 'ANULAR', 'Anular'
        RESTAURAR = 'RESTAURAR', 'Restaurar'

    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='acciones')
    accion = models.CharField(max_length=15, choices=Accion.choices)
    detalle = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'historial_accion'

    def __str__(self) -> str:
        return f'{self.get_accion_display()} · {self.usuario}'


class Reporte(models.Model):
    class Tipo(models.TextChoices):
        CERTIFICADO_TRIBUTARIO = 'CERTIFICADO_TRIBUTARIO', 'Certificado tributario'
        REPORTE_AUDITORIA = 'REPORTE_AUDITORIA', 'Reporte auditoría'
        EXPORTACION = 'EXPORTACION', 'Exportación'
        BACKUP = 'BACKUP', 'Backup'

    class Formato(models.TextChoices):
        PDF = 'PDF', 'PDF'
        CSV = 'CSV', 'CSV'
        XLSX = 'XLSX', 'XLSX'
        JSON = 'JSON', 'JSON'
        ZIP = 'ZIP', 'ZIP'

    tipo = models.CharField(max_length=40, choices=Tipo.choices)
    formato = models.CharField(max_length=4, choices=Formato.choices, default=Formato.PDF)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name='reportes')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes')
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes')
    calificacion = models.ForeignKey(
        Calificacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes',
    )
    parametros = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'reportes'
        indexes = [
            models.Index(fields=['tipo', 'created_at'], name='idx_reportes_tipo_fecha'),
        ]

    def __str__(self) -> str:
        return f'Reporte {self.get_tipo_display()}'


class Sesion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    jwt_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    emitido_at = models.DateTimeField(default=timezone.now)
    expira_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'sesiones'

    def __str__(self) -> str:
        return f'Sesión {self.jwt_id or self.pk}'
