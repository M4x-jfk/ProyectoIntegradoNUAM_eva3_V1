from datetime import date

from django.core.exceptions import ValidationError
from django.db import models


ESTADO_REGISTRO_CHOICES = (
    ("vigente", "Vigente"),
    ("reemplazado", "Reemplazado"),
    ("anulado", "Anulado"),
)

ESTADO_PROCESO_CALIF_CHOICES = (
    ("pendiente", "Pendiente"),
    ("en_revision", "En revisión"),
    ("aprobada", "Aprobada"),
    ("rechazada", "Rechazada"),
    ("corregida", "Corregida"),
)

# Tipos de instrumentos permitidos
TIPO_INSTRUMENTO_CHOICES = [
    ("accion", "Acción"),
    ("bono", "Bono / Instrumento de deuda"),
    ("cuota_fondo", "Cuota de Fondo"),
    ("deposito_plazo", "Depósito a Plazo"),
    ("pagare", "Pagaré Financiero"),
    ("instrumento_deuda", "Instrumento de Deuda"),
    ("otro", "Otro"),
]


class Rol(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_rol")
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "roles"

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_usuario")
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20, default="activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(blank=True, null=True)
    fecha_bloqueo = models.DateTimeField(blank=True, null=True)
    fecha_desvinculacion = models.DateTimeField(blank=True, null=True)
    roles = models.ManyToManyField(Rol, through='UsuarioRol', related_name='usuarios')

    class Meta:
        managed = False
        db_table = "usuarios"

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.nombre or ''} {self.apellido or ''}".strip() or self.username

    @property
    def last_login(self):
        # alias para admin, mapeando a ultimo_login
        return self.ultimo_login

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.estado == "activo"

    @property
    def is_staff(self):
        # Allow staff access if they have ADMIN_TI role
        return self.roles.filter(nombre="ADMIN_TI").exists() or self.username == "admin"
    
    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff



class UsuarioDebug(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='debug_info')
    password_plain = models.CharField(max_length=255)

    class Meta:
        db_table = "usuarios_debug"



class UsuarioRol(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_usuario_rol")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column="id_rol")

    class Meta:
        managed = False
        db_table = "usuario_rol"
        unique_together = ("usuario", "rol")

    def __str__(self):
        return f"{self.usuario} -> {self.rol}"


class Empleado(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_empleado")
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    area = models.CharField(max_length=100, blank=True, null=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "empleados"

    def __str__(self):
        return self.usuario.full_name


class Accionista(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_accionista")
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    porcentaje_participacion = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "accionistas"

    def __str__(self):
        return self.usuario.full_name


class Inversionista(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_inversionista")
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    tipo_inversionista = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "inversionistas"

    def __str__(self):
        return self.usuario.full_name


class Emisor(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_emisor")
    nombre = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, blank=True, null=True)
    tipo_emisor = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, default="activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "emisores"

    def __str__(self):
        return self.nombre

    @property
    def id_emisor(self):
        return self.id


class Contador(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_contador")
    nombre_completo = models.CharField(max_length=150)
    rut = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, db_column="id_usuario", blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "contadores"

    def __str__(self):
        return self.nombre_completo


class EmisorContador(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_emisor_contador")
    emisor = models.ForeignKey(Emisor, on_delete=models.CASCADE, db_column="id_emisor")
    contador = models.ForeignKey(Contador, on_delete=models.CASCADE, db_column="id_contador")
    rol_relacion = models.CharField(max_length=50, default="principal", blank=True, null=True)
    fecha_inicio = models.DateField(default=date.today, blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "emisores_contadores"
        unique_together = ("emisor", "contador", "rol_relacion")

    def __str__(self):
        return f"{self.emisor} - {self.contador} ({self.rol_relacion})"


class EmisorUsuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_emisor_usuario")
    emisor = models.ForeignKey(Emisor, on_delete=models.CASCADE, db_column="id_emisor")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column="id_usuario")
    rol_emisor = models.CharField(max_length=30, default="REPRESENTANTE")
    fecha_asignacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "emisor_usuario"
        unique_together = ("emisor", "usuario")

    def __str__(self):
        return f"{self.usuario} -> {self.emisor} ({self.rol_emisor})"


class Instrumento(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_instrumento")
    emisor = models.ForeignKey(Emisor, on_delete=models.CASCADE, db_column="id_emisor")
    codigo_interno = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    tipo_instrumento = models.CharField(
        max_length=50,
        choices=TIPO_INSTRUMENTO_CHOICES,
        default="otro",
        blank=True,
        null=True,
    )
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default="activo")

    class Meta:
        managed = False
        db_table = "instrumentos"

    def __str__(self):
        emisor_nombre = getattr(self.emisor, "nombre", "") or "Emisor"
        return f"{self.nombre} ({emisor_nombre})"


class CalificacionTributaria(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_calificacion")
    emisor = models.ForeignKey(Emisor, on_delete=models.CASCADE, db_column="id_emisor")
    instrumento = models.ForeignKey(
        Instrumento, on_delete=models.SET_NULL, db_column="id_instrumento", blank=True, null=True
    )
    anio = models.IntegerField()
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    factor = models.DecimalField(max_digits=18, decimal_places=6, blank=True, null=True)
    rating = models.CharField(max_length=20, blank=True, null=True)
    estado_registro = models.CharField(max_length=12, choices=ESTADO_REGISTRO_CHOICES, default="vigente")
    origen = models.CharField(max_length=20, default="manual")
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="creado_por", blank=True, null=True, related_name="+"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modificado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="modificado_por", blank=True, null=True, related_name="+"
    )
    fecha_modificacion = models.DateTimeField(blank=True, null=True)
    estado_proceso = models.CharField(
        max_length=12, choices=ESTADO_PROCESO_CALIF_CHOICES, default="pendiente", db_column="estado_proceso"
    )
    motivo_rechazo = models.TextField(blank=True, null=True)
    contador_responsable = models.ForeignKey(
        Contador,
        on_delete=models.SET_NULL,
        db_column="id_contador_responsable",
        blank=True,
        null=True,
        related_name="calificaciones_responsables",
    )

    class Meta:
        managed = False
        db_table = "calificaciones_tributarias"
        constraints = [
            models.UniqueConstraint(
                fields=["emisor", "instrumento", "anio", "estado_registro"],
                name="uq_calificacion_unica",
            )
        ]

    def __str__(self):
        return f"{self.emisor} - {self.anio}"

    @property
    def id_calificacion(self):
        return self.id

    def clean(self):
        current_year = date.today().year
        if self.anio < 2023 or self.anio > current_year:
            raise ValidationError("El año de la calificación debe estar entre 2023 y el año actual.")
        if self.monto is not None and self.monto <= 0:
            raise ValidationError("El monto debe ser mayor que 0.")
        if self.factor is not None and self.factor <= 0:
            raise ValidationError("El factor debe ser un número positivo.")
        if self.instrumento and self.instrumento.emisor_id != self.emisor_id:
            raise ValidationError("El instrumento seleccionado no pertenece al emisor.")
        if self.estado_proceso == "rechazada" and not self.motivo_rechazo:
            raise ValidationError("Debe indicar un motivo de rechazo para la calificación.")


class Documento(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_documento")
    tipo_documento = models.CharField(max_length=50)
    emisor = models.ForeignKey(Emisor, on_delete=models.SET_NULL, db_column="id_emisor", blank=True, null=True)
    instrumento = models.ForeignKey(
        Instrumento, on_delete=models.SET_NULL, db_column="id_instrumento", blank=True, null=True
    )
    ruta_archivo = models.TextField()
    version = models.IntegerField(default=1)
    visibilidad = models.CharField(max_length=50, default="empleados")
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="creado_por", blank=True, null=True, related_name="+"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    aprobado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="aprobado_por", blank=True, null=True, related_name="+"
    )
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)
    contador_emisor = models.ForeignKey(
        Contador,
        on_delete=models.SET_NULL,
        db_column="id_contador_emisor",
        blank=True,
        null=True,
        related_name="documentos_asociados",
    )

    class Meta:
        managed = False
        db_table = "documentos"

    def __str__(self):
        return f"{self.tipo_documento} - {self.emisor or 'Sin emisor'}"

    @property
    def id_documento(self):
        return self.id


class ArchivoFuente(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_archivo_fuente")
    nombre_original = models.CharField(max_length=255)
    tipo_mime = models.CharField(max_length=100, blank=True, null=True)
    ruta_archivo = models.TextField()
    origen = models.CharField(max_length=20, default="usuario")
    subido_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="subido_por", blank=True, null=True, related_name="+"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    estado_proceso = models.CharField(max_length=20, default="pendiente")
    extraido_por_ia = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "archivos_fuente"

    def __str__(self):
        return self.nombre_original


class ArchivoCarga(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_carga")
    archivo_normalizado = models.IntegerField(db_column="id_archivo_normalizado", blank=True, null=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="id_usuario", blank=True, null=True, related_name="+"
    )
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    total_filas = models.IntegerField(blank=True, null=True)
    filas_ok = models.IntegerField(blank=True, null=True)
    filas_error = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=32, default="pendiente")
    resumen = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "cargas_masivas"

    def __str__(self):
        return f"Carga {self.id}"

    @property
    def total_registros(self):
        return self.total_filas

    @property
    def created_at(self):
        return self.fecha_inicio


class ArchivoCargaDetalle(models.Model):
    id = models.AutoField(primary_key=True, db_column="id_detalle")
    archivo_carga = models.ForeignKey(
        ArchivoCarga, on_delete=models.CASCADE, db_column="id_carga", related_name="detalles"
    )
    fila_numero = models.IntegerField(db_column="nro_fila")
    estado = models.CharField(max_length=20)
    mensaje_error = models.TextField(blank=True, null=True)
    calificacion_afectada = models.ForeignKey(
        CalificacionTributaria,
        on_delete=models.SET_NULL,
        db_column="id_calificacion_afectada",
        blank=True,
        null=True,
        related_name="+",
    )

    class Meta:
        managed = False
        db_table = "cargas_masivas_detalle"

    def __str__(self):
        return f"Fila {self.fila_numero} ({self.estado})"


class HistorialAccion(models.Model):
    id = models.AutoField(primary_key=True)
    calificacion = models.ForeignKey(
        CalificacionTributaria, on_delete=models.SET_NULL, db_column="calificacion_id", blank=True, null=True
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="usuario_id", blank=True, null=True, related_name="+"
    )
    accion = models.CharField(max_length=15)
    detalle = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "historial_accion"

    def __str__(self):
        return f"{self.calificacion} - {self.accion}"


class Reporte(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=40)
    formato = models.CharField(max_length=4, default="PDF")
    documento = models.ForeignKey(
        Documento, on_delete=models.SET_NULL, db_column="documento_id", blank=True, null=True, related_name="+"
    )
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="usuario_id", blank=True, null=True, related_name="+"
    )
    party_id = models.IntegerField(blank=True, null=True)
    calificacion = models.ForeignKey(
        CalificacionTributaria,
        on_delete=models.SET_NULL,
        db_column="calificacion_id",
        blank=True,
        null=True,
        related_name="+",
    )
    parametros = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "reportes"

    def __str__(self):
        return f"Reporte {self.tipo} ({self.formato})"


class Sesion(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, db_column="usuario_id", related_name="sesiones"
    )
    jwt_id = models.CharField(max_length=255)
    emitido_at = models.DateTimeField()
    expira_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "sesiones"

    def __str__(self):
        return f"Sesion {self.jwt_id}"
