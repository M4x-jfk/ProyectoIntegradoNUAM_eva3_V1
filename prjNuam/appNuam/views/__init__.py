"""
Enrutador de vistas por dominio.
"""
from .seguridad_views import LoginView, LogoutView, SwitchRoleView
from .dashboards_views import (
    DashboardAdminView,
    DashboardAnalistaView,
    DashboardSupervisorView,
    DashboardAccionistaView,
    DashboardInversionistaView,
    PowerBIPlaceholderView,
)
from .calificaciones_views import (
    CalificacionListView,
    CalificacionCreateView,
    CalificacionUpdateView,
    CalificacionDeleteView,
    CalificacionDetailView,
    CalificacionHistorialView,
    CalificacionExportView,
    AprobacionListView,
    AprobacionUpdateView,
)
from .usuarios_views import (
    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioToggleEstadoView,
    PerfilView,
)
from .documentos_views import (
    DocumentoListView,
    DocumentoUploadView,
    DocumentoDetailView,
    InformeOficialDownloadView,
)
from .auditoria_views import AuditoriaGlobalListView, BackupEstadoView
from .configuracion_views import ParametrosSistemaView, LogsBackupsView
from .future_views import (
    CargaMasivaPlaceholderView,
    IAPipelinePlaceholderView,
    FuturePowerBIPlaceholderView,
)

__all__ = [
    'LoginView', 'LogoutView', 'SwitchRoleView',
    'DashboardAdminView', 'DashboardAnalistaView', 'DashboardSupervisorView',
    'DashboardAccionistaView', 'DashboardInversionistaView', 'PowerBIPlaceholderView',
    'CalificacionListView', 'CalificacionCreateView', 'CalificacionUpdateView',
    'CalificacionDeleteView', 'CalificacionDetailView', 'CalificacionHistorialView',
    'CalificacionExportView', 'AprobacionListView', 'AprobacionUpdateView',
    'UsuarioListView', 'UsuarioCreateView', 'UsuarioUpdateView', 'UsuarioToggleEstadoView',
    'PerfilView',
    'DocumentoListView', 'DocumentoUploadView', 'DocumentoDetailView', 'InformeOficialDownloadView',
    'AuditoriaGlobalListView', 'BackupEstadoView',
    'ParametrosSistemaView', 'LogsBackupsView',
    'CargaMasivaPlaceholderView', 'IAPipelinePlaceholderView', 'FuturePowerBIPlaceholderView',
]
