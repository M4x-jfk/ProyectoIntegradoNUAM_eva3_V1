from django.db import models
from django.utils import timezone


class Rol(models.Model):
    """Roles del sistema (tabla roles)."""

    id_rol = models.AutoField(primary_key=True, db_column='id_rol')
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self) -> str:
        return self.nombre


class Usuario(models.Model):
    """Usuarios alineado a tabla usuarios con roles en tabla usuario_rol."""

    class Estado(models.TextChoices):
        ACTIVO = 'activo', 'Activo'
        INACTIVO = 'inactivo', 'Inactivo'
        BLOQUEADO = 'bloqueado', 'Bloqueado'
        DESVINCULADO = 'desvinculado', 'Desvinculado'

    id_usuario = models.AutoField(primary_key=True, db_column='id_usuario')
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.ACTIVO)
    fecha_creacion = models.DateTimeField(default=timezone.now, db_column='fecha_creacion')
    last_login = models.DateTimeField(null=True, blank=True, db_column='ultimo_login')
    fecha_bloqueo = models.DateTimeField(null=True, blank=True, db_column='fecha_bloqueo')
    fecha_desvinculacion = models.DateTimeField(null=True, blank=True, db_column='fecha_desvinculacion')
    roles = models.ManyToManyField('Rol', through='UsuarioRol', related_name='usuarios')

    class Meta:
        managed = False
        db_table = 'usuarios'
        indexes = [
            models.Index(fields=['email'], name='idx_usuarios_email'),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.estado == self.Estado.ACTIVO

    @property
    def roles_list(self):
        return list(self.roles.values_list('nombre', flat=True))


class UsuarioRol(models.Model):
    """Relación muchos a muchos usuarios/roles."""

    id_usuario_rol = models.AutoField(primary_key=True, db_column='id_usuario_rol')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario', related_name='rel_roles')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='id_rol', related_name='rel_usuarios')

    class Meta:
        managed = False
        db_table = 'usuario_rol'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'rol'], name='uniq_usuario_rol'),
        ]

    def __str__(self) -> str:
        return f'{self.usuario} - {self.rol}'


class Sesion(models.Model):
    """Control básico de sesiones (no usado aún)."""

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones', db_column='id_usuario')
    jwt_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    emitido_at = models.DateTimeField(default=timezone.now)
    expira_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'sesiones'

    def __str__(self) -> str:
        return f'Sesion {self.jwt_id or self.pk}'
