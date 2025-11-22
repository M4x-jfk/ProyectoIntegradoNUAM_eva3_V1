from django.urls import path
from . import views_ia

urlpatterns = [
    # Archivos Fuente
    path('ia/archivos/subir/', views_ia.ia_archivos_fuente_upload, name='ia_archivos_fuente_upload'),
    path('ia/archivos/', views_ia.ia_archivos_fuente_list, name='ia_archivos_fuente_list'),
    path('ia/archivos/<int:pk>/', views_ia.ia_archivos_fuente_detail, name='ia_archivos_fuente_detail'),

    # Archivos Normalizados & Validación
    path('ia/normalizados/', views_ia.ia_archivos_normalizados_list, name='ia_archivos_normalizados_list'),
    path('ia/validacion/<int:pk>/', views_ia.ia_validacion_archivo, name='ia_validacion_archivo'),

    # Carga Masiva & Trazabilidad
    path('ia/carga-masiva/<int:pk>/', views_ia.ia_carga_masiva_resumen, name='ia_carga_masiva_resumen'),
    path('ia/trazabilidad/', views_ia.ia_trazabilidad, name='ia_trazabilidad'),

    # Power BI
    path('powerbi/general/', views_ia.powerbi_dashboard_general, name='powerbi_dashboard_general'),
    path('powerbi/ejecutivo/', views_ia.powerbi_dashboard_ejecutivo, name='powerbi_dashboard_ejecutivo'),
]
