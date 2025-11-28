from django.urls import path, include
from appNuam.views import (
    LoginView,
    LogoutView,
    SwitchRoleView,
    DashboardAdminView,
    DashboardAnalistaView,
    DashboardSupervisorView,
    DashboardAccionistaView,
    DashboardInversionistaView,
    PowerBIPlaceholderView,
    CalificacionListView,
    CalificacionCreateView,
    CalificacionUpdateView,
    CalificacionDeleteView,
    CalificacionDetailView,
    CalificacionHistorialView,
    CalificacionExportView,
    AprobacionListView,
    AprobacionUpdateView,
    UsuarioListView,
    UsuarioCreateView,
    UsuarioUpdateView,
    UsuarioToggleEstadoView,
    PerfilView,
    DocumentoListView,
    DocumentoUploadView,
    DocumentoDetailView,
    InformeOficialDownloadView,
    AuditoriaGlobalListView,
    BackupEstadoView,
    ParametrosSistemaView,
    LogsBackupsView,
    CargaMasivaPlaceholderView,
    IAPipelinePlaceholderView,
)

urlpatterns = [
    # Login & Logout
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('seguridad/rol/', SwitchRoleView.as_view(), name='switch_role'),

    # Dashboards por Rol
    path('dashboard/admin/', DashboardAdminView.as_view(), name='dashboard_admin'),
    path('dashboard/analista/', DashboardAnalistaView.as_view(), name='dashboard_analista'),
    path('dashboard/supervisor/', DashboardSupervisorView.as_view(), name='dashboard_supervisor'),
    path('dashboard/accionista/', DashboardAccionistaView.as_view(), name='dashboard_accionista'),
    path('dashboard/inversionista/', DashboardInversionistaView.as_view(), name='dashboard_inversionista'),
    path('dashboard/powerbi/', PowerBIPlaceholderView.as_view(), name='dashboard_powerbi'),

    # Calificaciones
    path('calificaciones/', CalificacionListView.as_view(), name='calificaciones_list'),
    path('calificaciones/nueva/', CalificacionCreateView.as_view(), name='calificaciones_create'),
    path('calificaciones/<int:pk>/editar/', CalificacionUpdateView.as_view(), name='calificaciones_update'),
    path('calificaciones/<int:pk>/eliminar/', CalificacionDeleteView.as_view(), name='calificaciones_delete'),
    path('calificaciones/<int:pk>/', CalificacionDetailView.as_view(), name='calificaciones_detail'),
    path('calificaciones/<int:pk>/historial/', CalificacionHistorialView.as_view(), name='calificaciones_historial'),
    path('calificaciones/exportar/', CalificacionExportView.as_view(), name='calificaciones_export'),
    path('calificaciones/aprobaciones/', AprobacionListView.as_view(), name='aprobaciones_list'),
    path('calificaciones/aprobaciones/<int:pk>/', AprobacionUpdateView.as_view(), name='aprobaciones_update'),

    # Usuarios
    path('usuarios/', UsuarioListView.as_view(), name='usuarios_list'),
    path('usuarios/nuevo/', UsuarioCreateView.as_view(), name='usuarios_create'),
    path('usuarios/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='usuarios_update'),
    path('usuarios/<int:pk>/estado/', UsuarioToggleEstadoView.as_view(), name='usuarios_toggle_estado'),
    path('perfil/', PerfilView.as_view(), name='perfil'),

    # Documentos
    path('documentos/', DocumentoListView.as_view(), name='documentos_list'),
    path('documentos/subir/', DocumentoUploadView.as_view(), name='documentos_upload'),
    path('documentos/<int:pk>/', DocumentoDetailView.as_view(), name='documentos_detail'),
    path('documentos/informes/<int:pk>/descargar/', InformeOficialDownloadView.as_view(), name='informe_descargar'),

    # Auditoria / Configuracion
    path('auditoria/', AuditoriaGlobalListView.as_view(), name='auditoria'),
    path('backups/', BackupEstadoView.as_view(), name='backups_estado'),
    path('configuracion/parametros/', ParametrosSistemaView.as_view(), name='parametros_sistema'),
    path('configuracion/logs-backups/', LogsBackupsView.as_view(), name='logs_backups'),

    # Future placeholders
    path('future/carga-masiva/', CargaMasivaPlaceholderView.as_view(), name='carga_masiva_placeholder'),
    path('future/ia-etl/', IAPipelinePlaceholderView.as_view(), name='ia_etl_placeholder'),

    # IA module (placeholders)
    path('', include('appNuam.urls_ia')),
]
