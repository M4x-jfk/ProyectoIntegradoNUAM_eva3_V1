from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView, View

from appNuam.forms.seguridad_forms import LoginForm
from appNuam.models import Usuario
from appNuam.services.roles import get_primary_role, get_dashboard_url_name


class LoginView(FormView):
    """HU15: login seguro con políticas básicas."""

    template_name = 'templatesApp/seguridad/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard_admin')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hide_chrome'] = True  # oculta navbar/sidebar en login
        return ctx

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(self.request, username=username, password=password)
        if user is None:
            messages.error(self.request, 'Credenciales inválidas o cuenta inactiva.')
            return self.form_invalid(form)

        if user.estado != Usuario.Estado.ACTIVO:
            messages.error(self.request, 'Cuenta inactiva/bloqueada.')
            return self.form_invalid(form)

        login(self.request, user)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        roles = user.roles_list
        active_role = get_primary_role(roles)
        if not active_role:
            messages.error(self.request, 'No tiene roles asignados.')
            return self.form_invalid(form)

        self.request.session['user_roles'] = roles
        self.request.session['active_role'] = active_role
        self.request.session['user_name'] = user.nombre
        self.request.session['user_email'] = user.email

        return redirect(self.get_success_url_for_role(active_role))

    def get_success_url_for_role(self, role: str):
        return reverse_lazy(get_dashboard_url_name(role))


class LogoutView(View):
    """HU15: logout."""

    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.flush()
        return redirect('login')


class RoleRequiredMixin(LoginRequiredMixin):
    """RBAC simple por lista de roles."""

    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        user_roles = request.session.get('user_roles', [])
        active_role = request.session.get('active_role') or get_primary_role(user_roles)

        if active_role and active_role not in user_roles:
            active_role = get_primary_role(user_roles)

        if self.allowed_roles and not any(role in self.allowed_roles for role in user_roles):
            messages.error(request, 'No tiene permisos para acceder a esta vista.')
            fallback = get_dashboard_url_name(active_role)
            return redirect(reverse_lazy(fallback))

        if active_role:
            request.session['active_role'] = active_role
        return super().dispatch(request, *args, **kwargs)


class LogoutConfirmView(LoginRequiredMixin, TemplateView):
    template_name = 'templatesApp/seguridad/logout_confirm.html'


class SwitchRoleView(LoginRequiredMixin, View):
    """Permite alternar el rol activo cuando el usuario tiene mas de uno."""

    def post(self, request, *args, **kwargs):
        roles = request.session.get('user_roles', [])
        new_role = request.POST.get('role')
        if new_role in roles:
            request.session['active_role'] = new_role
            messages.success(request, f'Cambiaste al rol {new_role}.')
            return redirect(reverse_lazy(get_dashboard_url_name(new_role)))

        messages.error(request, 'Rol no valido para este usuario.')
        fallback = get_primary_role(roles)
        return redirect(reverse_lazy(get_dashboard_url_name(fallback)))
