from django.views.generic import TemplateView
from .seguridad_views import RoleRequiredMixin


class CargaMasivaPlaceholderView(RoleRequiredMixin, TemplateView):
    """HU04/HU12 futuras versiones."""

    template_name = 'templatesApp/future_features/carga_masiva_placeholder.html'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR']


class IAPipelinePlaceholderView(RoleRequiredMixin, TemplateView):
    """HU21-HU30 futuras versiones IA/ETL."""

    template_name = 'templatesApp/future_features/ia_etl_placeholder.html'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR']


class FuturePowerBIPlaceholderView(RoleRequiredMixin, TemplateView):
    """HU28 placeholder adicional."""

    template_name = 'templatesApp/dashboards/powerbi_placeholder.html'
    allowed_roles = ['ADMIN_TI', 'ACCIONISTA', 'INVERSIONISTA', 'SUPERVISOR']
