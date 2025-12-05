from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def _role_names(user):
    names = set()
    if hasattr(user, "roles"):
        try:
            names.update([getattr(r, "nombre", str(r)) for r in user.roles.all()])
        except Exception:
            pass
    if hasattr(user, "role_names"):
        try:
            names.update(user.role_names)
        except Exception:
            pass
    if hasattr(user, "rol"):
        names.add(user.rol)
    if hasattr(user, "grupo"):
        names.add(user.grupo)
    return {n for n in names if n}


def role_required(*allowed_roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_roles = _role_names(request.user)
            if not allowed_roles or user_roles.intersection(set(allowed_roles)):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tiene permisos para acceder a esta sección.")

        return _wrapped_view

    return decorator


class RoleRequiredMixin:
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        user_roles = _role_names(request.user)
        if not request.user.is_authenticated and settings.DEBUG:
            # En modo DEBUG permitimos ver la vista sin autenticación para demo.
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
        if self.required_roles and not user_roles.intersection(set(self.required_roles)):
            return HttpResponseForbidden("No tiene permisos para acceder a esta sección.")
        return super().dispatch(request, *args, **kwargs)
