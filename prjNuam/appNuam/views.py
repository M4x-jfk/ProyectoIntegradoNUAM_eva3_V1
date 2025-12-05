from datetime import date, timedelta
import os

import requests
from requests import exceptions as req_exceptions
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import CalificacionTributariaForm
from .models import (
    CalificacionTributaria,
    Emisor,
    EmisorContador,
    EmisorUsuario,
    Instrumento,
)
from .permissions import RoleRequiredMixin, _role_names


# Configuración de indicadores disponibles por país
INDICADORES = {
    "chile": {
        "usd": {
            "tipo": "fx",
            "symbol": "CLP",
            "descripcion": "1 USD en CLP",
        },
        "uf": {
            "tipo": "mindicador",
            "endpoint": "https://mindicador.cl/api/uf",
            "descripcion": "UF",
        },
        "utm": {
            "tipo": "mindicador",
            "endpoint": "https://mindicador.cl/api/utm",
            "descripcion": "UTM",
        },
    },
    "colombia": {
        "usd": {
            "tipo": "fx",
            "symbol": "COP",
            "descripcion": "1 USD en COP",
        }
        # Espacio para agregar más indicadores en el futuro
    },
    "peru": {
        "usd": {
            "tipo": "fx",
            "symbol": "PEN",
            "descripcion": "1 USD en PEN",
        }
        # Espacio para agregar más indicadores en el futuro
    },
}


def landing_indicadores_view(request):
    """Renderiza la landing page de indicadores económicos."""
    return render(request, "templatesApp/landing_indicadores.html")


def _fetch_fx_timeseries(symbol: str) -> tuple[list[str], list[float]]:
    """
    Obtiene serie de tiempo (últimos ~30 días) para una moneda con exchangerate.host.
    Requiere ACCESS_KEY si la API lo exige (EXCHANGE_API_KEY en .env).
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=32)
    access_key = os.getenv("EXCHANGE_API_KEY")
    if not access_key:
        raise ValueError("Falta configurar EXCHANGE_API_KEY para consultar exchangerate.host")

    url = "https://api.exchangerate.host/timeseries"
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "base": "USD",
        "symbols": symbol,
        "access_key": access_key,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    try:
        payload = resp.json()
    except ValueError as exc:
        raise ValueError(f"No se pudo leer JSON de exchangerate.host: {exc}") from exc

    if payload.get("success") is False:
        err = payload.get("error", {})
        msg = err.get("info") or err or "API exchangerate.host respondió sin éxito"
        raise ValueError(f"API exchangerate.host: {msg}")

    if not payload.get("rates"):
        raise ValueError("No se encontraron datos de tasas de cambio")

    sorted_dates = sorted(payload["rates"].keys())
    labels = []
    values = []
    for date_key in sorted_dates:
        rate_info = payload["rates"].get(date_key, {})
        value = rate_info.get(symbol)
        if value is not None:
            labels.append(date_key)
            values.append(value)

    if not values:
        raise ValueError("La API no devolvió valores válidos para el indicador solicitado")

    return labels, values


def _fetch_mindicador_timeseries(endpoint: str) -> tuple[list[str], list[float]]:
    """Obtiene serie de tiempo (últimos ~30 puntos) desde mindicador.cl."""
    resp = requests.get(endpoint, timeout=10)
    resp.raise_for_status()
    try:
        payload = resp.json()
    except ValueError as exc:
        raise ValueError(f"No se pudo leer JSON de mindicador.cl: {exc}") from exc

    serie = payload.get("serie", [])
    if not serie:
        raise ValueError("No se encontraron datos en la API de mindicador.cl")

    # Tomamos los últimos ~30 elementos y los ordenamos por fecha ascendente
    last_points = sorted(serie[:30], key=lambda item: item.get("fecha"))
    labels = [item["fecha"][:10] for item in last_points if "fecha" in item]
    values = [item["valor"] for item in last_points if "valor" in item]

    if not values:
        raise ValueError("La API de mindicador.cl no devolvió valores válidos")

    return labels, values


def indicador_timeseries_api(request, pais: str, codigo: str):
    """
    Devuelve serie temporal para un indicador solicitado.
    Responde JSON con labels (fechas) y data (valores).
    """
    pais = (pais or "").lower()
    codigo = (codigo or "").lower()

    if pais not in INDICADORES or codigo not in INDICADORES[pais]:
        return JsonResponse({"error": "País o indicador no soportado"}, status=400)

    indicador_cfg = INDICADORES[pais][codigo]
    descripcion = indicador_cfg["descripcion"]

    try:
        if indicador_cfg["tipo"] == "fx":
            labels, data = _fetch_fx_timeseries(indicador_cfg["symbol"])
        elif indicador_cfg["tipo"] == "mindicador":
            labels, data = _fetch_mindicador_timeseries(indicador_cfg["endpoint"])
        else:
            return JsonResponse({"error": "Tipo de indicador no soportado"}, status=400)
    except req_exceptions.RequestException as exc:
        return JsonResponse({"error": f"Error al consultar API externa: {exc}"}, status=502)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=502)
    except Exception as exc:  # cobertura defensiva
        return JsonResponse({"error": f"Error inesperado: {exc}"}, status=500)

    return JsonResponse(
        {
            "pais": pais,
            "indicador": codigo,
            "descripcion": descripcion,
            "labels": labels,
            "data": data,
        }
    )


# ---------------------------------------------------------------------------
# Nuevas vistas del sistema NUAM – Mantenedor de Calificaciones Tributarias
# ---------------------------------------------------------------------------


class LandingView(TemplateView):
    template_name = "templatesApp/landing_public.html"


class LoginView(TemplateView):
    template_name = "templatesApp/auth/login.html"

    # TODO: implementar autenticación real (usar Django auth o integración existente)
    def post(self, request, *args, **kwargs):
        # Placeholder: integra aquí la autenticación real con tu backend.
        # Si el usuario ya está autenticado, redirige según rol.
        if request.user and request.user.is_authenticated:
            return redirect(_redirect_by_role(request.user))
        return self.get(request, *args, **kwargs)


def _redirect_by_role(user):
    """
    Devuelve el nombre de URL para redirigir según prioridad de rol.
    Prioridad: ADMIN_TI > SUPERVISOR > CONTADOR/ANALISTA > ACCIONISTA > INVERSIONISTA.
    """
    roles = {r.upper() for r in _role_names(user)}
    if "ADMIN_TI" in roles:
        return "admin_ti_dashboard"
    if "SUPERVISOR" in roles:
        return "supervisor_dashboard"
    if "CONTADOR" in roles or "ANALISTA" in roles:
        return "contador_dashboard"
    if "ACCIONISTA" in roles:
        return "accionista_dashboard"
    if "INVERSIONISTA" in roles:
        return "inversionista_dashboard"
    return "landing_public"


class RegistroExternoView(TemplateView):
    template_name = "templatesApp/auth/registro.html"

    # TODO: limitar roles a ACCIONISTA/INVERSIONISTA y crear usuario en BD externa


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("landing_public")


class AdminTiDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/dashboard.html"
    required_roles = ["ADMIN_TI"]


class AdminTiUsuariosListView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/usuarios_list.html"
    required_roles = ["ADMIN_TI"]

    # TODO: CRUD de usuarios internos (crear roles internos)


class AdminTiEmisoresListView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/emisores_list.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["emisores"] = Emisor.objects.all()
        return ctx


class AdminTiEmisorContadoresView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/emisor_contadores.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        emisor_id = kwargs.get("id_emisor")
        ctx["emisor"] = Emisor.objects.filter(pk=emisor_id).first()
        ctx["asignaciones"] = EmisorContador.objects.filter(emisor_id=emisor_id)
        return ctx


class AdminTiEmisorRepresentantesView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/emisor_representantes.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        emisor_id = kwargs.get("id_emisor")
        ctx["emisor"] = Emisor.objects.filter(pk=emisor_id).first()
        ctx["representantes"] = EmisorUsuario.objects.filter(emisor_id=emisor_id)
        return ctx


class ContadorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/contador/dashboard.html"
    required_roles = ["CONTADOR", "ANALISTA"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["calificaciones_pendientes"] = CalificacionTributaria.objects.filter(
            estado_proceso="pendiente"
        )[:10]
        return ctx


class ContadorCalificacionListView(RoleRequiredMixin, ListView):
    template_name = "templatesApp/contador/calificaciones_list.html"
    required_roles = ["CONTADOR", "ANALISTA"]
    model = CalificacionTributaria
    context_object_name = "calificaciones"

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CalificacionTributaria.objects.none()
        emisores_ids = EmisorContador.objects.filter(
            contador__usuario=self.request.user
        ).values_list("emisor_id", flat=True)
        return CalificacionTributaria.objects.filter(emisor_id__in=emisores_ids)


class ContadorCalificacionCreateView(RoleRequiredMixin, CreateView):
    template_name = "templatesApp/contador/calificacion_form.html"
    required_roles = ["CONTADOR", "ANALISTA"]
    form_class = CalificacionTributariaForm
    success_url = reverse_lazy("contador_calificaciones")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        emisores_ids = []
        if self.request.user.is_authenticated:
            emisores_ids = EmisorContador.objects.filter(
                contador__usuario=self.request.user
            ).values_list("emisor_id", flat=True)
        kwargs["usuario"] = self.request.user
        kwargs["emisores_permitidos"] = Emisor.objects.filter(id__in=emisores_ids)
        return kwargs


class ContadorCalificacionUpdateView(RoleRequiredMixin, UpdateView):
    template_name = "templatesApp/contador/calificacion_form.html"
    required_roles = ["CONTADOR", "ANALISTA"]
    form_class = CalificacionTributariaForm
    model = CalificacionTributaria
    success_url = reverse_lazy("contador_calificaciones")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        emisores_ids = []
        if self.request.user.is_authenticated:
            emisores_ids = EmisorContador.objects.filter(
                contador__usuario=self.request.user
            ).values_list("emisor_id", flat=True)
        kwargs["usuario"] = self.request.user
        kwargs["emisores_permitidos"] = Emisor.objects.filter(id__in=emisores_ids)
        return kwargs

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CalificacionTributaria.objects.none()
        emisores_ids = EmisorContador.objects.filter(
            contador__usuario=self.request.user
        ).values_list("emisor_id", flat=True)
        return CalificacionTributaria.objects.filter(
            emisor_id__in=emisores_ids, estado_registro="vigente"
        )


class SupervisorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/supervisor/dashboard.html"
    required_roles = ["SUPERVISOR"]


class SupervisorCalificacionListView(RoleRequiredMixin, ListView):
    template_name = "templatesApp/supervisor/calificaciones_list.html"
    required_roles = ["SUPERVISOR"]
    model = CalificacionTributaria
    context_object_name = "calificaciones"

    def get_queryset(self):
        return CalificacionTributaria.objects.all()


class AccionistaDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/accionista/dashboard.html"
    required_roles = ["ACCIONISTA"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            ctx["emisores"] = Emisor.objects.none()
            ctx["calificaciones"] = CalificacionTributaria.objects.none()
            return ctx
        emisor_ids = EmisorUsuario.objects.filter(usuario=self.request.user).values_list("emisor_id", flat=True)
        ctx["emisores"] = Emisor.objects.filter(id__in=emisor_ids)
        ctx["calificaciones"] = CalificacionTributaria.objects.filter(emisor_id__in=emisor_ids)[:20]
        return ctx


class InversionistaDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/inversionista/dashboard.html"
    required_roles = ["INVERSIONISTA"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            ctx["emisores"] = Emisor.objects.none()
            ctx["calificaciones"] = CalificacionTributaria.objects.none()
            return ctx
        emisor_ids = EmisorUsuario.objects.filter(usuario=self.request.user).values_list("emisor_id", flat=True)
        ctx["emisores"] = Emisor.objects.filter(id__in=emisor_ids)
        ctx["calificaciones"] = CalificacionTributaria.objects.filter(emisor_id__in=emisor_ids)[:20]
        return ctx


class EmisorCalificacionesView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/emisor/calificaciones.html"
    required_roles = ["ACCIONISTA", "INVERSIONISTA"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        emisor_id = kwargs.get("id_emisor")
        ctx["emisor"] = Emisor.objects.filter(pk=emisor_id).first()
        ctx["calificaciones"] = CalificacionTributaria.objects.filter(emisor_id=emisor_id)
        return ctx


class EmisorArchivoUploadView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/emisor/archivo_upload.html"
    required_roles = ["ACCIONISTA", "INVERSIONISTA"]

    # TODO: implementar formulario de carga y permisos vinculados a emisor_usuario

