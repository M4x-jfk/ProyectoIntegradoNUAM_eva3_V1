from django.urls import path

from .views import (
    AccionistaDashboardView,
    AdminTiDashboardView,
    AdminTiEmisorContadoresView,
    AdminTiEmisorRepresentantesView,
    AdminTiEmisoresListView,
    AdminTiUsuariosListView,
    ContadorCalificacionCreateView,
    ContadorCalificacionListView,
    ContadorCalificacionUpdateView,
    ContadorDashboardView,
    EmisorArchivoUploadView,
    EmisorCalificacionesView,
    InversionistaDashboardView,
    LandingView,
    LoginView,
    LogoutView,
    RegistroExternoView,
    SupervisorCalificacionListView,
    SupervisorDashboardView,
    indicador_timeseries_api,
    landing_indicadores_view,
)

urlpatterns = [
    # Públicas
    path("", LandingView.as_view(), name="landing_public"),
    path("login/", LoginView.as_view(), name="login"),
    path("accounts/login/", LoginView.as_view(), name="accounts_login"),
    path("registro/", RegistroExternoView.as_view(), name="registro_externo"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("indicadores/", landing_indicadores_view, name="landing_indicadores"),

    # API indicadores económicos
    path(
        "api/indicador/<str:pais>/<str:codigo>/",
        indicador_timeseries_api,
        name="indicador_timeseries_api",
    ),

    # ADMIN_TI
    path("admin-ti/dashboard/", AdminTiDashboardView.as_view(), name="admin_ti_dashboard"),
    path("admin-ti/usuarios/", AdminTiUsuariosListView.as_view(), name="admin_ti_usuarios"),
    path("admin-ti/emisores/", AdminTiEmisoresListView.as_view(), name="admin_ti_emisores"),
    path(
        "admin-ti/emisores/<int:id_emisor>/contadores/",
        AdminTiEmisorContadoresView.as_view(),
        name="admin_ti_emisor_contadores",
    ),
    path(
        "admin-ti/emisores/<int:id_emisor>/representantes/",
        AdminTiEmisorRepresentantesView.as_view(),
        name="admin_ti_emisor_representantes",
    ),

    # CONTADOR / ANALISTA
    path("contador/dashboard/", ContadorDashboardView.as_view(), name="contador_dashboard"),
    path("contador/calificaciones/", ContadorCalificacionListView.as_view(), name="contador_calificaciones"),
    path("contador/calificaciones/nueva/", ContadorCalificacionCreateView.as_view(), name="contador_calificacion_create"),
    path(
        "contador/calificaciones/<int:pk>/editar/",
        ContadorCalificacionUpdateView.as_view(),
        name="contador_calificacion_update",
    ),

    # SUPERVISOR
    path("supervisor/dashboard/", SupervisorDashboardView.as_view(), name="supervisor_dashboard"),
    path("supervisor/calificaciones/", SupervisorCalificacionListView.as_view(), name="supervisor_calificaciones"),

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
