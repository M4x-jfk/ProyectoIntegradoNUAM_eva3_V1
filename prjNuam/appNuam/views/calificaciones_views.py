from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)

from appNuam.forms.calificaciones_forms import CalificacionForm, AprobacionForm
from appNuam.models import Calificacion, CalificacionHistorial, Aprobacion
from appNuam.services.calculo_factor import calcular_factor
from appNuam.services.validaciones_negocio import validar_calificacion
from appNuam.services.auditoria_service import registrar_evento
from .seguridad_views import RoleRequiredMixin


class CalificacionListView(RoleRequiredMixin, ListView):
    """HU01-HU06: listado con filtros y export stub."""

    model = Calificacion
    template_name = 'templatesApp/calificaciones/listado.html'
    context_object_name = 'calificaciones'
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']

    def get_queryset(self):
        qs = Calificacion.objects.all()
        estado = self.request.GET.get('estado_registro')
        if estado:
            qs = qs.filter(estado_registro=estado)
        return qs.order_by('-fecha_creacion')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        roles = self.request.session.get('user_roles', [])
        ctx['can_manage_calif'] = any(r in ['ADMIN_TI', 'SUPERVISOR', 'ANALISTA'] for r in roles)
        return ctx


class CalificacionDetailView(RoleRequiredMixin, DetailView):
    model = Calificacion
    template_name = 'templatesApp/calificaciones/detalle.html'
    context_object_name = 'calificacion'
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI', 'ACCIONISTA', 'INVERSIONISTA']


class CalificacionCreateView(RoleRequiredMixin, CreateView):
    """HU01 + HU19 (calculo factor) + HU18 (validaciones)."""

    model = Calificacion
    form_class = CalificacionForm
    template_name = 'templatesApp/calificaciones/form.html'
    success_url = reverse_lazy('calificaciones_list')
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']

    def form_valid(self, form):
        calificacion = form.save(commit=False)
        calificacion.creado_por = self.request.user
        calificacion.factor = calcular_factor(calificacion)
        errores = validar_calificacion(calificacion)
        if errores:
            for error in errores:
                messages.error(self.request, error)
            return self.form_invalid(form)
        calificacion.save()
        registrar_evento(self.request.user, 'CALIFICACION_CREAR', objeto='Calificacion', objeto_id=calificacion.pk)
        return super().form_valid(form)


class CalificacionUpdateView(RoleRequiredMixin, UpdateView):
    """HU02 + HU19 + HU18."""

    model = Calificacion
    form_class = CalificacionForm
    template_name = 'templatesApp/calificaciones/form.html'
    success_url = reverse_lazy('calificaciones_list')
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']

    def form_valid(self, form):
        calificacion = form.save(commit=False)
        calificacion.modificado_por = self.request.user
        calificacion.fecha_modificacion = timezone.now()
        calificacion.factor = calcular_factor(calificacion)
        errores = validar_calificacion(calificacion)
        if errores:
            for error in errores:
                messages.error(self.request, error)
            return self.form_invalid(form)
        calificacion.save()
        registrar_evento(self.request.user, 'CALIFICACION_MODIFICAR', objeto='Calificacion', objeto_id=calificacion.pk)
        return super().form_valid(form)


class CalificacionDeleteView(RoleRequiredMixin, DeleteView):
    """HU03: eliminación lógica."""

    model = Calificacion
    template_name = 'templatesApp/calificaciones/confirm_delete.html'
    success_url = reverse_lazy('calificaciones_list')
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']

    def delete(self, request, *args, **kwargs):
        calificacion = self.get_object()
        calificacion.soft_delete(user=request.user)
        registrar_evento(request.user, 'CALIFICACION_ELIMINAR', objeto='Calificacion', objeto_id=calificacion.pk)
        return redirect(self.success_url)


class CalificacionHistorialView(RoleRequiredMixin, ListView):
    """HU06 timeline."""

    model = CalificacionHistorial
    template_name = 'templatesApp/calificaciones/historial.html'
    context_object_name = 'historial'
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI', 'ACCIONISTA', 'INVERSIONISTA']

    def get_queryset(self):
        return CalificacionHistorial.objects.filter(calificacion_id=self.kwargs['pk']).order_by('-created_at')


class CalificacionExportView(RoleRequiredMixin, View):
    """HU05 export stub."""

    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']

    def get(self, request, *args, **kwargs):
        # Placeholder simple: en futuro generar PDF/XLSX
        registrar_evento(request.user, 'CALIFICACION_EXPORTAR', objeto='Calificacion', objeto_id=None)
        response = HttpResponse('Export en construcción', content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="calificaciones.txt"'
        return response


class AprobacionListView(RoleRequiredMixin, ListView):
    """HU14 lista de aprobaciones pendientes."""

    model = Aprobacion
    template_name = 'templatesApp/calificaciones/aprobaciones_listado.html'
    context_object_name = 'aprobaciones'
    allowed_roles = ['SUPERVISOR', 'ADMIN_TI']

    def get_queryset(self):
        return Aprobacion.objects.filter(estado=Aprobacion.Estado.PENDIENTE)


class AprobacionUpdateView(RoleRequiredMixin, UpdateView):
    """HU14 actualizar aprobacion (aprobar/rechazar)."""

    model = Aprobacion
    form_class = AprobacionForm
    template_name = 'templatesApp/calificaciones/aprobacion_form.html'
    success_url = reverse_lazy('aprobaciones_list')
    allowed_roles = ['SUPERVISOR', 'ADMIN_TI']

    def form_valid(self, form):
        aprobacion = form.save(commit=False)
        aprobacion.aprobador = self.request.user
        aprobacion.save()
        registrar_evento(
            self.request.user,
            'CALIFICACION_APROBAR' if aprobacion.estado == Aprobacion.Estado.APROBADA else 'CALIFICACION_RECHAZAR',
            objeto='Calificacion',
            objeto_id=aprobacion.calificacion_id,
        )
        return super().form_valid(form)
