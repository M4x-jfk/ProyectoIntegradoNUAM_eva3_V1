from django.urls import path, include
from . import views

urlpatterns = [
    # Login & Logout
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards por Rol
    path('dashboard/admin/', views.dashboard_admin_view, name='dashboard_admin'),
    path('dashboard/analista/', views.dashboard_analista_view, name='dashboard_analista'),
    path('dashboard/supervisor/', views.dashboard_supervisor_view, name='dashboard_supervisor'),
    path('dashboard/accionista/', views.dashboard_accionista_view, name='dashboard_accionista'),
    path('dashboard/inversionista/', views.dashboard_inversionista_view, name='dashboard_inversionista'),

    # Vistas Placeholder
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('partys/', views.partys_view, name='partys'),
    path('calificaciones/', views.calificaciones_view, name='calificaciones'),
    path('carga-masiva/', views.carga_masiva_view, name='carga_masiva'),
    path('auditoria/', views.auditoria_view, name='auditoria'),
    path('reportes/', views.reportes_view, name='reportes'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
    path('perfil/', views.perfil_view, name='perfil'),

    # IA Module
    path('', include('appNuam.urls_ia')),
]
