from django.contrib import admin

from . import models


@admin.register(models.Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombre', 'estado', 'last_login_at')
    list_filter = ('estado',)
    search_fields = ('correo', 'nombre')


@admin.register(models.UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')


@admin.register(models.Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('filename', 'formato', 'size_bytes', 'created_at')
    list_filter = ('formato',)
    search_fields = ('filename', 'storage_uri')


@admin.register(models.Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('nombre_legal', 'rut', 'tipo', 'email_contacto')
    list_filter = ('tipo',)
    search_fields = ('nombre_legal', 'rut')


@admin.register(models.ArchivoCarga)
class ArchivoCargaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'total_registros', 'created_at')
    list_filter = ('estado',)
    search_fields = ('documento__filename',)


@admin.register(models.Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'party', 'monto', 'estado', 'fuente', 'fecha')
    list_filter = ('estado', 'fuente')
    search_fields = ('id', 'party__nombre_legal')


@admin.register(models.ArchivoCargaDetalle)
class ArchivoCargaDetalleAdmin(admin.ModelAdmin):
    list_display = ('archivo_carga', 'fila_numero', 'estado')
    list_filter = ('estado',)


@admin.register(models.HistorialAccion)
class HistorialAccionAdmin(admin.ModelAdmin):
    list_display = ('calificacion', 'usuario', 'accion', 'created_at')
    list_filter = ('accion',)


@admin.register(models.Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'formato', 'usuario', 'created_at')
    list_filter = ('tipo', 'formato')


@admin.register(models.Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'jwt_id', 'emitido_at', 'expira_at')
