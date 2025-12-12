from django.urls import path

from .views import (
    AccionistaDashboardView,
    AdminTiDashboardView,
    AdminTiEmisorContadoresView,
    AdminTiEmisorRepresentantesView,
    AdminTiEmisoresListView,
    AdminTiEmisorCreateView,
    AdminTiEmisorContadorCreateView,
    AdminTiEmisorContadorDeleteView,
    AdminTiEmisorUsuarioCreateView,
    AdminTiEmisorUsuarioDeleteView,
    AdminTiUsuariosListView,
    AdminTiUserCreateView,
    AdminTiUserUpdateView,
    AdminTiUserDeleteView,
    ContadorCalificacionCreateView,
    ContadorCalificacionListView,
    ContadorCalificacionUpdateView,
    ContadorDashboardView,
    EmisorArchivoUploadView,
    EmisorCalificacionesView,
    crear_calificacion,
    InversionistaDashboardView,
    LandingView,
    LoginView,
    LogoutView,
    RegistroExternoView,
    SupervisorCalificacionListView,
    SupervisorDashboardView,
    SupervisorCalificacionEstadoUpdateView,
    indicador_timeseries_api,
    landing_indicadores_view,
    GenerarReporteCalificacionesView,
)

urlpatterns = [
    # Públicas
    path("", LandingView.as_view(), name="landing_public"),
    path("login/", LoginView.as_view(), name="login"),
    path("accounts/login/", LoginView.as_view(), name="accounts_login"),
    path("registro/", RegistroExternoView.as_view(), name="registro_externo"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("indicadores/", landing_indicadores_view, name="landing_indicadores"),

    # PDF Reports
    path("reportes/calificaciones/<int:id_emisor>/", GenerarReporteCalificacionesView.as_view(), name="reporte_calificaciones_pdf"),

    # API indicadores económicos
    path(
        "api/indicador/<str:pais>/<str:codigo>/",
        indicador_timeseries_api,
        name="indicador_timeseries_api",
    ),

    # ADMIN_TI
    path("admin-ti/dashboard/", AdminTiDashboardView.as_view(), name="admin_ti_dashboard"),
    path("admin-ti/usuarios/", AdminTiUsuariosListView.as_view(), name="admin_ti_usuarios"),
    path("admin-ti/usuarios/crear/", AdminTiUserCreateView.as_view(), name="admin_ti_user_create"),
    path("admin-ti/usuarios/<int:pk>/editar/", AdminTiUserUpdateView.as_view(), name="admin_ti_user_update"),
    path("admin-ti/usuarios/<int:pk>/eliminar/", AdminTiUserDeleteView.as_view(), name="admin_ti_user_delete"),
    path("admin-ti/emisores/", AdminTiEmisoresListView.as_view(), name="admin_ti_emisores"),
    path("admin-ti/emisores/crear/", AdminTiEmisorCreateView.as_view(), name="admin_ti_emisor_create"),
    path(
        "admin-ti/emisores/<int:id_emisor>/contadores/",
        AdminTiEmisorContadoresView.as_view(),
        name="admin_ti_emisor_contadores",
    ),
    path(
        "admin-ti/emisores/<int:id_emisor>/contadores/agregar/",
        AdminTiEmisorContadorCreateView.as_view(),
        name="admin_ti_emisor_contador_create",
    ),
    path(
        "admin-ti/emisores/contadores/<int:pk>/eliminar/",
        AdminTiEmisorContadorDeleteView.as_view(),
        name="admin_ti_emisor_contador_delete",
    ),
    path(
        "admin-ti/emisores/<int:id_emisor>/representantes/",
        AdminTiEmisorRepresentantesView.as_view(),
        name="admin_ti_emisor_representantes",
    ),
    path(
        "admin-ti/emisores/<int:id_emisor>/representantes/agregar/",
        AdminTiEmisorUsuarioCreateView.as_view(),
        name="admin_ti_emisor_representante_create",
    ),
    path(
        "admin-ti/emisores/representantes/<int:pk>/eliminar/",
        AdminTiEmisorUsuarioDeleteView.as_view(),
        name="admin_ti_emisor_representante_delete",
    ),

    # CONTADOR / ANALISTA
    path("contador/dashboard/", ContadorDashboardView.as_view(), name="contador_dashboard"),
    path("contador/calificaciones/", ContadorCalificacionListView.as_view(), name="contador_calificaciones"),
    path("contador/calificaciones/nueva/", ContadorCalificacionCreateView.as_view(), name="contador_calificacion_create"),
    path("calificaciones/crear/", crear_calificacion, name="calificacion_crear"),
    path(
        "contador/calificaciones/<int:pk>/editar/",
        ContadorCalificacionUpdateView.as_view(),
        name="contador_calificacion_update",
    ),

    # SUPERVISOR
    path("supervisor/dashboard/", SupervisorDashboardView.as_view(), name="supervisor_dashboard"),
    path("supervisor/calificaciones/", SupervisorCalificacionListView.as_view(), name="supervisor_calificaciones"),
    path(
        "supervisor/calificaciones/<int:pk>/estado/",
        SupervisorCalificacionEstadoUpdateView.as_view(),
        name="supervisor_calificacion_estado",
    ),

    # ACCIONISTA / INVERSIONISTA
    path("accionista/dashboard/", AccionistaDashboardView.as_view(), name="accionista_dashboard"),
    path("inversionista/dashboard/", InversionistaDashboardView.as_view(), name="inversionista_dashboard"),
    path(
        "emisor/<int:id_emisor>/calificaciones/",
        EmisorCalificacionesView.as_view(),
        name="emisor_calificaciones",
    ),
    path(
        "emisor/<int:id_emisor>/archivos/subir/",
        EmisorArchivoUploadView.as_view(),
        name="emisor_archivo_upload",
    ),
]
