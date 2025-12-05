def nuam_globals(request):
    """
    Context processor básico para variables globales.
    Amplía según las necesidades de branding o configuración.
    """
    return {}


def roles_context(request):
    """
    Expone los roles del usuario autenticado para usarlos en plantillas.
    """
    roles = []
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        if hasattr(user, "roles"):
            try:
                roles = [getattr(r, "nombre", str(r)) for r in user.roles.all()]
            except Exception:
                roles = []
        elif hasattr(user, "rol"):
            roles = [user.rol]
    return {"user_roles": roles}
