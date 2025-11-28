from django.contrib import admin

from . import models


@admin.register(models.Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


@admin.register(models.Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'nombre', 'estado', 'last_login')
    list_filter = ('estado',)
    search_fields = ('username', 'email', 'nombre', 'apellido')


@admin.register(models.UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol')


@admin.register(models.Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('id_documento', 'tipo_documento', 'ruta_archivo', 'version', 'fecha_creacion')
    list_filter = ('visibilidad',)
    search_fields = ('ruta_archivo', 'tipo_documento')


@admin.register(models.Emisor)
class EmisorAdmin(admin.ModelAdmin):
    list_display = ('id_emisor', 'nombre', 'rut', 'tipo_emisor', 'estado')
    list_filter = ('estado', 'tipo_emisor')
    search_fields = ('nombre', 'rut')


@admin.register(models.ArchivoCarga)
class ArchivoCargaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'total_registros', 'created_at')
    list_filter = ('estado',)
    search_fields = ('documento__filename',)


@admin.register(models.Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('id_calificacion', 'emisor', 'instrumento', 'anio', 'monto', 'estado_registro', 'origen')
    list_filter = ('estado_registro', 'origen')
    search_fields = ('id_calificacion', 'emisor__nombre')


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
