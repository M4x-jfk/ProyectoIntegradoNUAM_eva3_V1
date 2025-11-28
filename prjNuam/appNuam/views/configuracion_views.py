from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from appNuam.forms.calificaciones_forms import ParametroSistemaForm
from appNuam.models import ParametroSistema, ReglaNegocio
from appNuam.services.parametros_service import actualizar_parametro
from appNuam.services.auditoria_service import registrar_evento
from .seguridad_views import RoleRequiredMixin


class ParametrosSistemaView(RoleRequiredMixin, FormView):
    """HU16/HU19: parametrizacion tributaria."""

    template_name = 'templatesApp/configuracion/parametros_sistema.html'
    form_class = ParametroSistemaForm
    success_url = reverse_lazy('parametros_sistema')
    allowed_roles = ['ADMIN_TI']

    def get_initial(self):
        initial = super().get_initial()
        param = ParametroSistema.objects.order_by('-version').first()
        if param:
            initial['clave'] = param.clave
            initial['valor'] = param.valor
            initial['tipo'] = param.tipo
            initial['descripcion'] = param.descripcion
        return initial

    def form_valid(self, form):
        param = actualizar_parametro(form.cleaned_data)
        registrar_evento(self.request.user, 'PARAMETRO_ACTUALIZAR', objeto='ParametroSistema', objeto_id=param.pk)
        messages.success(self.request, 'Parámetros guardados.')
        return super().form_valid(form)


class LogsBackupsView(RoleRequiredMixin, TemplateView):
    """HU20: estado de logs/backups ya atendido en BackupEstadoView template compartida."""

    template_name = 'templatesApp/configuracion/logs_backups.html'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR']

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            # Se evalúa inmediatamente para evitar errores diferidos en template si la tabla no existe
            ctx['reglas'] = list(ReglaNegocio.objects.filter(activo=True))
        except Exception:
            ctx['reglas'] = []
        ctx['backup'] = None
        return ctx
