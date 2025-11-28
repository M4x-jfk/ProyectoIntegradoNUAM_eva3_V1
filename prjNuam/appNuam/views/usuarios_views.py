from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View

from appNuam.forms.usuarios_forms import UsuarioForm
from appNuam.models import Usuario
from .seguridad_views import RoleRequiredMixin


class UsuarioListView(RoleRequiredMixin, ListView):
    """HU09 listado usuarios + activacion/desactivacion."""

    model = Usuario
    template_name = 'templatesApp/usuarios/listado.html'
    context_object_name = 'usuarios'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR']


class UsuarioCreateView(RoleRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'templatesApp/usuarios/form.html'
    success_url = reverse_lazy('usuarios_list')
    allowed_roles = ['ADMIN_TI']


class UsuarioUpdateView(RoleRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'templatesApp/usuarios/form.html'
    success_url = reverse_lazy('usuarios_list')
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR']


class UsuarioToggleEstadoView(RoleRequiredMixin, View):
    """Activar/desactivar/bloquear en vez de borrar (regla)."""

    allowed_roles = ['ADMIN_TI']

    def post(self, request, *args, **kwargs):
        user = Usuario.objects.get(pk=kwargs['pk'])
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado not in Usuario.Estado.values:
            messages.error(request, 'Estado inválido.')
            return redirect('usuarios_list')
        user.estado = nuevo_estado
        user.save(update_fields=['estado'])
        messages.success(request, 'Estado actualizado.')
        return redirect('usuarios_list')


class PerfilView(RoleRequiredMixin, DetailView):
    """Perfil propio HU11."""

    model = Usuario
    template_name = 'templatesApp/usuarios/perfil.html'
    context_object_name = 'usuario'
    allowed_roles = ['ADMIN_TI', 'SUPERVISOR', 'ANALISTA', 'ACCIONISTA', 'INVERSIONISTA']

    def get_object(self, queryset=None):
        return self.request.user
