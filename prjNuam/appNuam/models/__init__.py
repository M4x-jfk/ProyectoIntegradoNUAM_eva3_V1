"""
Modelos organizados por dominio.
HU: ver comentarios en cada archivo.
"""
from .usuarios import Rol, Usuario, UsuarioRol, Sesion
from .calificaciones import Emisor, Instrumento, Calificacion, CalificacionHistorial, Aprobacion
from .documentos import Documento, ArchivoCarga, ArchivoCargaDetalle, InformeOficial
from .auditoria import AuditoriaEvento, Reporte, HistorialAccion, BackupEstado
from .parametros import ParametroSistema, ReglaNegocio

__all__ = [
    'Rol', 'Usuario', 'UsuarioRol', 'Sesion',
    'Emisor', 'Instrumento', 'Calificacion', 'CalificacionHistorial', 'Aprobacion',
    'Documento', 'ArchivoCarga', 'ArchivoCargaDetalle', 'InformeOficial',
    'AuditoriaEvento', 'Reporte', 'HistorialAccion', 'BackupEstado',
    'ParametroSistema', 'ReglaNegocio',
]
