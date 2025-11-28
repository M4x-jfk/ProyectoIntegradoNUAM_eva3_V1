from django.views.generic import ListView, TemplateView

from appNuam.models import AuditoriaEvento, BackupEstado
from .seguridad_views import RoleRequiredMixin


class AuditoriaGlobalListView(RoleRequiredMixin, ListView):
    """HU10: tabla de eventos auditable."""

    model = AuditoriaEvento
    template_name = 'templatesApp/auditoria/global.html'
    context_object_name = 'eventos'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR']

    def get_queryset(self):
        qs = AuditoriaEvento.objects.all().order_by('-created_at')
        accion = self.request.GET.get('accion')
        if accion:
            qs = qs.filter(accion=accion)
        return qs


class BackupEstadoView(RoleRequiredMixin, TemplateView):
    """HU20: estado de logs y backups."""

    template_name = 'templatesApp/configuracion/logs_backups.html'
    allowed_roles = ['ADMIN_TI']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['backup'] = BackupEstado.objects.order_by('-created_at').first()
        return ctx
