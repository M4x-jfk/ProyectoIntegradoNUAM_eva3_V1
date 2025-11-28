from django.utils import timezone
from django.views.generic import TemplateView

from appNuam.models import (
    Usuario,
    Rol,
    Documento,
    ArchivoCarga,
    Calificacion,
)
from .seguridad_views import RoleRequiredMixin


class DashboardAdminView(RoleRequiredMixin, TemplateView):
    """HU07/HU11: dashboard para admin TI."""

    template_name = 'templatesApp/dashboards/dashboard_admin.html'
    allowed_roles = ['ADMIN_TI']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['usuarios_count'] = Usuario.objects.count()
        ctx['usuarios_activos'] = Usuario.objects.filter(estado=Usuario.Estado.ACTIVO).count()
        ctx['roles_count'] = Rol.objects.count()
        ctx['ultimos_docs'] = Documento.objects.order_by('-fecha_creacion')[:5]
        return ctx


class DashboardAnalistaView(RoleRequiredMixin, TemplateView):
    """HU07/HU11: dashboard analista."""

    template_name = 'templatesApp/dashboards/dashboard_analista.html'
    allowed_roles = ['ANALISTA']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx['cargas_pendientes'] = ArchivoCarga.objects.filter(estado=ArchivoCarga.Estado.EN_PROCESO).count()
            ctx['cargas_fallidas'] = ArchivoCarga.objects.filter(estado=ArchivoCarga.Estado.FALLIDA).count()
        except Exception:
            # Si la tabla de cargas no existe en este entorno, evitar romper el dashboard
            ctx['cargas_pendientes'] = 0
            ctx['cargas_fallidas'] = 0
        ctx['mis_docs'] = Documento.objects.filter(creado_por_id=self.request.user.pk).order_by('-fecha_creacion')[:5]
        return ctx


class DashboardSupervisorView(RoleRequiredMixin, TemplateView):
    """HU07/HU11: dashboard supervisor."""

    template_name = 'templatesApp/dashboards/dashboard_supervisor.html'
    allowed_roles = ['SUPERVISOR']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['calificaciones_pendientes'] = Calificacion.objects.filter(
            estado_registro=Calificacion.EstadoRegistro.VIGENTE
        ).count()
        hoy = timezone.now().date()
        try:
            ctx['cargas_hoy'] = ArchivoCarga.objects.filter(created_at__date=hoy).count()
        except Exception:
            ctx['cargas_hoy'] = 0
        return ctx


class DashboardAccionistaView(RoleRequiredMixin, TemplateView):
    """HU07 dashboard ejecutivo."""

    template_name = 'templatesApp/dashboards/dashboard_ejecutivo.html'
    allowed_roles = ['ACCIONISTA']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_calificaciones'] = Calificacion.objects.filter(
            estado_registro=Calificacion.EstadoRegistro.VIGENTE
        ).count()
        ctx['powerbi_url'] = None
        return ctx


class DashboardInversionistaView(RoleRequiredMixin, TemplateView):
    """HU08 dashboard estrategico."""

    template_name = 'templatesApp/dashboards/dashboard_estrategico.html'
    allowed_roles = ['INVERSIONISTA']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_calificaciones'] = Calificacion.objects.filter(
            estado_registro=Calificacion.EstadoRegistro.VIGENTE
        ).count()
        ctx['powerbi_url'] = None
        return ctx


class PowerBIPlaceholderView(RoleRequiredMixin, TemplateView):
    """HU28 placeholder Power BI (sin integracion real)."""

    template_name = 'templatesApp/dashboards/powerbi_placeholder.html'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR', 'ACCIONISTA', 'INVERSIONISTA']
