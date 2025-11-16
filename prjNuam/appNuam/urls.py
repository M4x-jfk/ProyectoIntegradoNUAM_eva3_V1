from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('partys/', views.partys_view, name='partys'),
    path('calificaciones/', views.calificaciones_view, name='calificaciones'),
    path('carga-masiva/', views.carga_masiva_view, name='carga_masiva'),
    path('auditoria/', views.auditoria_view, name='auditoria'),
]
