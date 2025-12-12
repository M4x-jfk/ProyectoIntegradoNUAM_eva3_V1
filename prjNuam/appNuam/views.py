from datetime import date, timedelta
import hashlib
import logging
import os

import requests
from requests import exceptions as req_exceptions
from django.contrib.auth import logout, login as auth_login
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, DeleteView
from rest_framework.views import APIView

from .forms import (
    CalificacionTributariaForm,
    UsuarioForm,
    EmisorForm,
    EmisorContadorForm,
    EmisorUsuarioForm,
    RegistroUsuarioForm,
    SupervisorEstadoForm,
)
from .models import (
    CalificacionTributaria,
    Emisor,
    EmisorContador,
    EmisorUsuario,
    Instrumento,
    Usuario,
    UsuarioRol,
    Rol,
    Accionista,
    Inversionista,
    Documento,
    HistorialAccion,
)
from .permissions import RoleRequiredMixin, _role_names

from django.db import transaction
from django.contrib.auth import login as auth_login


logger = logging.getLogger(__name__)


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


def crear_calificacion(request):
    """
    Vista simple para crear calificaciones tributarias desde un formulario standalone.
    Carga emisores, instrumentos y contadores de forma dinámica.
    """
    form = CalificacionTributariaForm(request.POST or None, usuario=request.user)
    if request.method == "POST" and form.is_valid():
        calif = form.save()
        _registrar_historial(calif, request.user, "CREACION", "Creación de calificación tributaria")
        messages.success(
            request,
            "La calificación tributaria fue creada correctamente y está en estado Pendiente. "
            "Debe ser revisada por un supervisor o contador responsable.",
        )
        return redirect("contador_calificaciones")
    return render(request, "templatesApp/calificaciones/crear.html", {"form": form})


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


def _registrar_historial(calif: CalificacionTributaria, usuario, accion: str, detalle: str = ""):
    """
    Registra una entrada de historial para trazabilidad.
    No revienta el flujo si falla.
    """
    try:
        HistorialAccion.objects.create(
            calificacion=calif,
            usuario=usuario if getattr(usuario, "is_authenticated", False) else None,
            accion=accion[:15],
            detalle=detalle,
        )
    except Exception as exc:
        logger.warning("No se pudo registrar historial: %s", exc)


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
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        demo_password = os.getenv("DEMO_DEFAULT_PASSWORD", "1234")
        demo_hash = hashlib.sha256(demo_password.encode("utf-8")).hexdigest()

        usuarios = list(Usuario.objects.all().order_by("username"))
        for user in usuarios:
            if getattr(user, "password_hash", None) == demo_hash:
                user.demo_password = demo_password

        ctx["usuarios_demo"] = usuarios
        ctx["demo_default_password"] = demo_password
        return ctx

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        ctx = self.get_context_data(**kwargs)

        if not username or not password:
            ctx["error"] = "Debe ingresar usuario y contraseña."
            return self.render_to_response(ctx)

        try:
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            ctx["error"] = "Usuario o contraseña inválidos."
            logger.warning("ADMIN_ALERT login failed: usuario '%s' no existe", username)
            return self.render_to_response(ctx)

        candidate_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if user.password_hash != candidate_hash:
            ctx["error"] = "Usuario o contraseña inválidos."
            logger.warning("ADMIN_ALERT login failed: contraseña inválida para usuario '%s'", username)
            return self.render_to_response(ctx)

        estado = (user.estado or "").lower()
        if estado in {"bloqueado", "inactivo"}:
            ctx["error"] = f"El usuario está {estado}; inicio de sesión bloqueado."
            logger.warning(
                "ADMIN_ALERT intento de inicio de sesión por usuario %s con estado %s",
                username,
                estado,
            )
            return self.render_to_response(ctx)

        # Autenticar sesión Django con backend custom
        try:
            user.backend = "appNuam.auth_backends.SHA256Backend"
            auth_login(request, user)
        except Exception as exc:
            logger.warning("ADMIN_ALERT no se pudo iniciar sesión en Django auth: %s", exc)

        target = _redirect_by_role(user)
        logger.info(
            "ADMIN_ALERT usuario '%s' inició sesión, redirigiendo a %s, estado=%s",
            username,
            target,
            estado or "activo",
        )
        return redirect(target)


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


class RegistroExternoView(CreateView):
    template_name = "templatesApp/auth/registro.html"
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy("landing_public")

    def form_valid(self, form):
        with transaction.atomic():
            # 1. Crear Usuario
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            user.password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
            user.save()
            
            tipo_cuenta = form.cleaned_data.get("tipo_cuenta")
            emisores = form.cleaned_data.get("emisores")

            # 2. Asignar Rol
            rol_nombre = tipo_cuenta.upper() # ACCIONISTA or INVERSIONISTA
            rol_obj, _ = Rol.objects.get_or_create(nombre=rol_nombre)
            UsuarioRol.objects.create(usuario=user, rol=rol_obj)

            # 3. Crear Perfil específico
            if tipo_cuenta == "accionista":
                Accionista.objects.create(usuario=user)
                # 4. Vincular Emisores
                if emisores:
                    for em in emisores:
                        EmisorUsuario.objects.create(
                            usuario=user,
                            emisor=em,
                            rol_emisor="ACCIONISTA"
                        )
            else:
                Inversionista.objects.create(usuario=user, tipo_inversionista="Retail")

            # Auto-login (simulado pues usamos password_hash custom)
            # En un sistema real django auth: auth_login(self.request, user)
            # Aquí redirigimos al login con mensaje
            
            return redirect("login")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("landing_public")


class AdminTiDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/dashboard.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_usuarios"] = Usuario.objects.count()
        ctx["total_emisores"] = Emisor.objects.count()
        ctx["total_calificaciones"] = CalificacionTributaria.objects.count()
        # La BD enum admite: pendiente, terminada, rechazada. Map en_revision/corregida -> pendiente, aprobada -> terminada
        ctx["calif_pendientes"] = CalificacionTributaria.objects.filter(estado_proceso="pendiente").count()
        ctx["calif_en_revision"] = ctx["calif_pendientes"]
        ctx["calif_aprobadas"] = CalificacionTributaria.objects.filter(estado_proceso="terminada").count()
        ctx["calif_rechazadas"] = CalificacionTributaria.objects.filter(estado_proceso="rechazada").count()
        return ctx


class AdminTiUsuariosListView(RoleRequiredMixin, ListView):
    template_name = "templatesApp/admin/usuarios_list.html"
    required_roles = ["ADMIN_TI"]
    model = Usuario
    context_object_name = "usuarios"

    def get_queryset(self):
        return Usuario.objects.all().order_by("-fecha_creacion")


class AdminTiUserCreateView(RoleRequiredMixin, CreateView):
    template_name = "templatesApp/admin/usuario_form.html"
    required_roles = ["ADMIN_TI"]
    form_class = UsuarioForm
    success_url = reverse_lazy("admin_ti_usuarios")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        # Check if user has CONTADOR or ANALISTA role
        if user.roles.filter(nombre__in=["CONTADOR", "ANALISTA"]).exists():
            fullname = user.full_name or user.username
            Contador.objects.get_or_create(
                usuario=user, 
                defaults={"nombre_completo": fullname, "email": user.email}
            )
        return response


class AdminTiUserUpdateView(RoleRequiredMixin, UpdateView):
    template_name = "templatesApp/admin/usuario_form.html"
    required_roles = ["ADMIN_TI"]
    form_class = UsuarioForm
    model = Usuario
    success_url = reverse_lazy("admin_ti_usuarios")


class AdminTiUserDeleteView(RoleRequiredMixin, DeleteView):
    template_name = "templatesApp/admin/usuario_confirm_delete.html"
    required_roles = ["ADMIN_TI"]
    model = Usuario
    success_url = reverse_lazy("admin_ti_usuarios")


class AdminTiEmisoresListView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/emisores_list.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["emisores"] = Emisor.objects.all()
        return ctx


class AdminTiEmisorCreateView(RoleRequiredMixin, CreateView):
    template_name = "templatesApp/admin/emisor_form.html"
    required_roles = ["ADMIN_TI"]
    form_class = EmisorForm
    success_url = reverse_lazy("admin_ti_emisores")


class AdminTiEmisorContadoresView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/emisor_contadores.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        emisor_id = kwargs.get("id_emisor")
        ctx["emisor"] = Emisor.objects.filter(pk=emisor_id).first()
        ctx["asignaciones"] = EmisorContador.objects.filter(emisor_id=emisor_id)
        return ctx


class AdminTiEmisorContadorCreateView(RoleRequiredMixin, CreateView):
    template_name = "templatesApp/admin/emisor_contador_form.html"
    required_roles = ["ADMIN_TI"]
    form_class = EmisorContadorForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.emisor = Emisor.objects.get(pk=self.kwargs["id_emisor"])
        kwargs["emisor"] = self.emisor
        return kwargs

    def form_valid(self, form):
        form.instance.emisor = self.emisor
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["emisor"] = self.emisor
        return ctx

    def get_success_url(self):
        return reverse_lazy("admin_ti_emisor_contadores", kwargs={"id_emisor": self.emisor.id})


class AdminTiEmisorContadorDeleteView(RoleRequiredMixin, DeleteView):
    template_name = "templatesApp/admin/confirm_delete_generic.html"
    required_roles = ["ADMIN_TI"]
    model = EmisorContador
    
    def get_success_url(self):
        return reverse_lazy("admin_ti_emisor_contadores", kwargs={"id_emisor": self.object.emisor.id})


class AdminTiEmisorRepresentantesView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/admin/emisor_representantes.html"
    required_roles = ["ADMIN_TI"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        emisor_id = kwargs.get("id_emisor")
        ctx["emisor"] = Emisor.objects.filter(pk=emisor_id).first()
        ctx["representantes"] = EmisorUsuario.objects.filter(emisor_id=emisor_id)
        return ctx


class AdminTiEmisorUsuarioCreateView(RoleRequiredMixin, CreateView):
    template_name = "templatesApp/admin/emisor_representante_form.html"
    required_roles = ["ADMIN_TI"]
    form_class = EmisorUsuarioForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.emisor = Emisor.objects.get(pk=self.kwargs["id_emisor"])
        kwargs["emisor"] = self.emisor
        return kwargs

    def form_valid(self, form):
        form.instance.emisor = self.emisor
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["emisor"] = self.emisor
        return ctx

    def get_success_url(self):
        return reverse_lazy("admin_ti_emisor_representantes", kwargs={"id_emisor": self.emisor.id})


class AdminTiEmisorUsuarioDeleteView(RoleRequiredMixin, DeleteView):
    template_name = "templatesApp/admin/confirm_delete_generic.html"
    required_roles = ["ADMIN_TI"]
    model = EmisorUsuario
    
    def get_success_url(self):
        return reverse_lazy("admin_ti_emisor_representantes", kwargs={"id_emisor": self.object.emisor.id})


class ContadorDashboardView(RoleRequiredMixin, TemplateView):
    template_name = "templatesApp/contador/dashboard.html"
    required_roles = ["CONTADOR", "ANALISTA"]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        emisores_ids = []
        if self.request.user.is_authenticated:
            emisores_ids = EmisorContador.objects.filter(
                contador__usuario=self.request.user
            ).values_list("emisor_id", flat=True)
        base_qs = CalificacionTributaria.objects.filter(emisor_id__in=emisores_ids) if emisores_ids else CalificacionTributaria.objects.all()
        ctx["calificaciones_pendientes"] = base_qs.filter(estado_proceso="pendiente")[:10]
        ctx["total_mis_emisores"] = len(emisores_ids)
        ctx["mis_calif_pendientes"] = base_qs.filter(estado_proceso="pendiente").count()
        ctx["mis_calif_en_revision"] = ctx["mis_calif_pendientes"]
        ctx["mis_calif_aprobadas"] = base_qs.filter(estado_proceso="terminada").count()
        ctx["mis_calif_rechazadas"] = base_qs.filter(estado_proceso="rechazada").count()
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
        # Si no hay emisores asignados (o usuario no autenticado), permite todos para evitar listas vacías
        kwargs["emisores_permitidos"] = Emisor.objects.filter(id__in=emisores_ids) if emisores_ids else Emisor.objects.all()
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
        kwargs["emisores_permitidos"] = Emisor.objects.filter(id__in=emisores_ids) if emisores_ids else Emisor.objects.all()
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["calif_pendientes"] = CalificacionTributaria.objects.filter(estado_proceso="pendiente").count()
        ctx["calif_en_revision"] = ctx["calif_pendientes"]
        ctx["calif_aprobadas"] = CalificacionTributaria.objects.filter(estado_proceso="terminada").count()
        ctx["calif_rechazadas"] = CalificacionTributaria.objects.filter(estado_proceso="rechazada").count()
        ctx["calif_total"] = CalificacionTributaria.objects.count()
        return ctx


class SupervisorCalificacionListView(RoleRequiredMixin, ListView):
    template_name = "templatesApp/supervisor/calificaciones_list.html"
    required_roles = ["SUPERVISOR"]
    model = CalificacionTributaria
    context_object_name = "calificaciones"

    def get_queryset(self):
        return CalificacionTributaria.objects.all()


class SupervisorCalificacionEstadoUpdateView(RoleRequiredMixin, UpdateView):
    template_name = "templatesApp/supervisor/calificacion_estado_form.html"
    required_roles = ["SUPERVISOR"]
    model = CalificacionTributaria
    form_class = SupervisorEstadoForm
    success_url = reverse_lazy("supervisor_calificaciones")

    def form_valid(self, form):
        calif = form.save(commit=False)
        calif.modificado_por = self.request.user if self.request.user.is_authenticated else None
        calif.fecha_modificacion = timezone.now()
        calif.save()
        form.save_m2m()
        _registrar_historial(
            calif,
            self.request.user,
            "ESTADO_SUP",
            f"Cambio de estado a {calif.estado_proceso}",
        )
        messages.success(self.request, "Estado actualizado correctamente.")
        return redirect(self.get_success_url())


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
        context = super().get_context_data(**kwargs)
        # Fetch actual reports from Documento model
        context["reportes"] = Documento.objects.filter(
            tipo_documento__icontains="reporte"
        ).order_by("-fecha_creacion")[:5]
        
        # Show all active issuers since "Follow" logic is not fully implemented for Inversionista
        # Or filter if using EmisorUsuario in future
        context["emisores"] = Emisor.objects.filter(estado="activo").order_by("nombre")
        return context


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import FileResponse
import io

class GenerarReporteCalificacionesView(RoleRequiredMixin, APIView):
    required_roles = ["INVERSIONISTA", "ACCIONISTA"] # Allow both

    def get(self, request, id_emisor):
        emisor = Emisor.objects.get(pk=id_emisor)
        calificaciones = CalificacionTributaria.objects.filter(emisor=emisor, estado_registro="vigente")

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setTitle(f"Reporte Calificaciones - {emisor.nombre}")

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 750, f"Reporte de Calificaciones Tributarias")
        p.setFont("Helvetica", 12)
        p.drawString(50, 730, f"Emisor: {emisor.nombre}")
        p.drawString(50, 715, f"RUT: {emisor.rut}")
        
        y = 680
        
        if not calificaciones.exists():
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Sin Calificaciones")
        else:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Año")
            p.drawString(100, y, "Instrumento")
            p.drawString(300, y, "Monto")
            p.drawString(400, y, "Factor")
            p.drawString(500, y, "Rating")
            y -= 20
            p.line(50, y+15, 550, y+15)
            
            p.setFont("Helvetica", 10)
            for cal in calificaciones:
                instr_nombre = cal.instrumento.nombre if cal.instrumento else "N/A"
                p.drawString(50, y, str(cal.anio))
                p.drawString(100, y, instr_nombre[:35]) # Truncate if long
                p.drawString(300, y, str(cal.monto))
                p.drawString(400, y, str(cal.factor) if cal.factor else "-")
                p.drawString(500, y, cal.rating or "-")
                y -= 20
                
                if y < 50:
                    p.showPage()
                    y = 750

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"reporte_{emisor.id}.pdf")



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
