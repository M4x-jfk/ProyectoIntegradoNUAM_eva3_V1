"""Helpers para manejo de roles y pantallas principales."""

from __future__ import annotations

from typing import Iterable

# Se define un orden de prioridad para elegir el rol activo
ROLE_PRIORITY = ['ADMIN_TI', 'SUPERVISOR', 'ANALISTA', 'ACCIONISTA', 'INVERSIONISTA']

# Mapa entre roles y el nombre de la URL de su dashboard
ROLE_HOME = {
    'ADMIN_TI': 'dashboard_admin',
    'SUPERVISOR': 'dashboard_supervisor',
    'ANALISTA': 'dashboard_analista',
    'ACCIONISTA': 'dashboard_accionista',
    'INVERSIONISTA': 'dashboard_inversionista',
}


def get_primary_role(roles: Iterable[str]) -> str | None:
    """Devuelve el rol con mayor prioridad dentro de una lista de roles."""
    for role in ROLE_PRIORITY:
        if role in roles:
            return role
    return None


def get_dashboard_url_name(role: str | None) -> str:
    """Nombre de url del dashboard segun rol (fallback a analista)."""
    if role is None:
        return ROLE_HOME['ANALISTA']
    return ROLE_HOME.get(role, ROLE_HOME['ANALISTA'])
