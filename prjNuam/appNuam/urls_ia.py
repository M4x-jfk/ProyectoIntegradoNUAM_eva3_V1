from django.urls import path
from appNuam.views.future_views import (
    CargaMasivaPlaceholderView,
    IAPipelinePlaceholderView,
    FuturePowerBIPlaceholderView,
)

urlpatterns = [
    # Futuras versiones IA/ETL/HU21-HU30 y cargas masivas HU04/HU12
    path('ia/', IAPipelinePlaceholderView.as_view(), name='ia_placeholder'),
    path('ia/carga-masiva/<int:pk>/', CargaMasivaPlaceholderView.as_view(), name='ia_carga_masiva_resumen'),
    path('ia/trazabilidad/', IAPipelinePlaceholderView.as_view(), name='ia_trazabilidad'),

    # Power BI placeholder HU28
    path('powerbi/general/', FuturePowerBIPlaceholderView.as_view(), name='powerbi_dashboard_general'),
    path('powerbi/ejecutivo/', FuturePowerBIPlaceholderView.as_view(), name='powerbi_dashboard_ejecutivo'),
]
