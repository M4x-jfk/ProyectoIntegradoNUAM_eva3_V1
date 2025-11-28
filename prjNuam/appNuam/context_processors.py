"""Contexto comun para roles en templates."""

from appNuam.services.roles import get_primary_role, get_dashboard_url_name


def roles_context(request):
    roles = request.session.get('user_roles', [])
    active_role = request.session.get('active_role') or get_primary_role(roles)
    if active_role and active_role not in roles:
        active_role = get_primary_role(roles)
    home_url_name = get_dashboard_url_name(active_role)
    return {
        'session_roles': roles,
        'active_role': active_role,
        'role_home_url': home_url_name,
    }
