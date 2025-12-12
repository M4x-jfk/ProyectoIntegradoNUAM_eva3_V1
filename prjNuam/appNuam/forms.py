from datetime import date

from django import forms
from django.utils import timezone

from .models import (
    CalificacionTributaria,
    Instrumento,
    Usuario,
    Rol,
    UsuarioRol,
    Emisor,
    Contador,
    EmisorContador,
    EmisorUsuario,
)


class CalificacionTributariaForm(forms.ModelForm):
    class Meta:
        model = CalificacionTributaria
        fields = [
            "emisor",
            "instrumento",
            "anio",
            "monto",
            "factor",
            "rating",
            "estado_proceso",
            "motivo_rechazo",
            "contador_responsable",
        ]
        help_texts = {
            "emisor": (
                "Seleccione la empresa que emitió el instrumento y entregó el certificado tributario "
                "correspondiente. Solo emisores creados y activos."
            ),
            "instrumento": (
                "Seleccione el instrumento financiero (acción, bono, fondo, etc.) asociado al emisor. "
                "Solo se mostrarán instrumentos registrados para el emisor elegido."
            ),
            "anio": (
                "Año tributario del certificado. Debe estar entre 2023 y el año actual; no se permiten años futuros."
            ),
            "monto": (
                "Monto informado por el emisor en el certificado tributario (dividendo, interés u otro valor base). "
                "Debe ser numérico y positivo."
            ),
            "factor": (
                "Factor tributario resultante de la conversión del monto según normas vigentes. Debe ser decimal válido; "
                "puede ser opcional si el sistema lo calcula."
            ),
            "rating": "Clasificación tributaria asociada (opcional).",
            "estado_proceso": (
                "Etapa del proceso (pendiente, aprobada, rechazada, etc.). Si se marca rechazada, indique motivo."
            ),
            "motivo_rechazo": "Justificación del rechazo; obligatorio solo si el estado es rechazada.",
            "contador_responsable": (
                "Profesional responsable de validar esta calificación. Se asigna automáticamente al contador/analista "
                "logueado; debe estar activo y vinculado."
            ),
        }
        help_texts = {
            "emisor": "Seleccione la empresa que emitió el instrumento y entregó el certificado tributario correspondiente.",
            "instrumento": "Seleccione el instrumento financiero (acción, bono, fondo, etc.) al que corresponde la calificación tributaria.",
            "anio": "Indique el año tributario al que pertenece la calificación (generalmente el año del certificado del emisor).",
            "monto": "Ingrese el monto informado por el emisor en su certificado tributario (dividendo, interés u otro valor base).",
            "factor": "Ingrese el factor tributario resultante de convertir el monto según las normas tributarias vigentes.",
            "rating": "Clasificación tributaria asociada al tratamiento del monto convertido (si aplica en el proceso del emisor).",
            "estado_proceso": "Indica en qué etapa se encuentra la calificación (pendiente, aprobada, rechazada, etc.).",
            "motivo_rechazo": "Justificación del rechazo de la calificación, en caso de inconsistencias o datos incorrectos.",
            "contador_responsable": "Profesional responsable de validar los datos tributarios asociados a este emisor e instrumento.",
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario", None)
        self.emisores_permitidos = kwargs.pop("emisores_permitidos", None)
        super().__init__(*args, **kwargs)
        # Emisores disponibles: los permitidos o todos
        self.fields["emisor"].queryset = (self.emisores_permitidos or Emisor.objects.all()).order_by("nombre")
        self.fields["instrumento"].queryset = Instrumento.objects.none() # Default empty

        if "emisor" in self.data:
            try:
                emisor_id = int(self.data.get("emisor"))
                self.fields["instrumento"].queryset = Instrumento.objects.filter(emisor_id=emisor_id).order_by("nombre")
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields["instrumento"].queryset = Instrumento.objects.filter(emisor=self.instance.emisor).order_by("nombre")
        else:
            # If no specific filtering required initially, allows all or empty. 
            # User requirement: "Solo los instrumentos existentes" (associated to Emisor usually, but initially can list all or wait for JS)
            # Better UX: Empty until Emisor selected, or All if no Emisor field restriction. 
            # However, standard Django is to allow all if not filtered.
            # But let's follow the logic: if we have emisores_permitidos, filter instruments too.
            if self.emisores_permitidos:
                self.fields["instrumento"].queryset = Instrumento.objects.filter(emisor__in=self.emisores_permitidos).order_by("nombre")
            else:
                 self.fields["instrumento"].queryset = Instrumento.objects.all().order_by("nombre")


        # Contador responsable: auto-asigna el contador/analista logueado y oculta el campo
        self.fields["contador_responsable"].required = False
        self.fields["contador_responsable"].queryset = Contador.objects.all().order_by("nombre_completo", "id")
        self.fields["contador_responsable"].widget = forms.HiddenInput()

        self._request_contador = None
        if self.usuario and getattr(self.usuario, "is_authenticated", False):
            self._request_contador = Contador.objects.filter(usuario=self.usuario).first()
            if self._request_contador:
                self.fields["contador_responsable"].initial = self._request_contador
        elif self.instance and self.instance.pk:
            self.fields["contador_responsable"].initial = self.instance.contador_responsable

        # Widget dinámico para año
        current_year = date.today().year
        self.fields["anio"].widget = forms.NumberInput(attrs={"min": 2023, "max": current_year, "step": 1})

    def clean_anio(self):
        anio = self.cleaned_data.get("anio")
        current_year = date.today().year
        if anio is None:
             return anio
        if anio < 2023:
            raise forms.ValidationError("El año no puede ser menor a 2023.")
        if anio > current_year:
            raise forms.ValidationError(f"El año no puede ser mayor al año actual ({current_year}).")
        return anio

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is None or monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que 0.")
        return monto

    def clean_factor(self):
        factor = self.cleaned_data.get("factor")
        if factor is not None and factor <= 0:
            raise forms.ValidationError("El factor debe ser un número positivo.")
        return factor

    def clean(self):
        cleaned = super().clean()
        emisor = cleaned.get("emisor")
        instrumento = cleaned.get("instrumento")
        estado_proceso = cleaned.get("estado_proceso")
        motivo_rechazo = cleaned.get("motivo_rechazo")

        if instrumento and emisor and instrumento.emisor_id != emisor.id:
            self.add_error("instrumento", "El instrumento seleccionado no pertenece al emisor.")

        if estado_proceso == "rechazada" and not motivo_rechazo:
            self.add_error("motivo_rechazo", "Debe indicar un motivo de rechazo.")

        # Determinar contador responsable:
        # 1) el contador ligado al usuario logueado
        # 2) si no hay y el emisor tiene un solo contador asignado, usarlo
        contador_resp = cleaned.get("contador_responsable") or self._request_contador
        if not contador_resp and emisor:
            qs_emisor_cont = EmisorContador.objects.filter(emisor=emisor).select_related("contador")
            # Si el usuario está ligado a algún contador de este emisor, usarlo
            if self.usuario and getattr(self.usuario, "is_authenticated", False):
                vinculo = qs_emisor_cont.filter(contador__usuario=self.usuario).first()
                if vinculo:
                    contador_resp = vinculo.contador
            # Como fallback, si hay un único contador para el emisor, úsalo
            if not contador_resp and qs_emisor_cont.count() == 1:
                unico = qs_emisor_cont.first()
                contador_resp = unico.contador

        if not contador_resp:
            self.add_error(
                "contador_responsable",
                "No se pudo determinar el contador responsable. Vincule el usuario a un contador activo o asigne un único contador al emisor.",
            )
        else:
            cleaned["contador_responsable"] = contador_resp

        return cleaned

    def save(self, commit=True):
        calif = super().save(commit=False)
        # Estado inicial pendiente y creador/modificador
        if not calif.pk:
            calif.estado_proceso = "pendiente"
            if self.usuario and getattr(self.usuario, "is_authenticated", False):
                calif.creado_por = self.usuario
        if self.usuario and getattr(self.usuario, "is_authenticated", False):
            calif.modificado_por = self.usuario
            calif.fecha_modificacion = timezone.now()
        if commit:
            calif.save()
            self.save_m2m()
        return calif


class SupervisorEstadoForm(forms.ModelForm):
    class Meta:
        model = CalificacionTributaria
        fields = ["estado_proceso", "motivo_rechazo"]
        help_texts = {
            "estado_proceso": "Cambie el estado de la calificación (Pendiente, En revisión, Aprobada, Rechazada, Corregida).",
            "motivo_rechazo": "Obligatorio si el estado es Rechazada.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar a valores aceptados por el enum de BD: pendiente, terminada, rechazada
        self.fields["estado_proceso"].choices = [
            ("pendiente", "Pendiente"),
            ("terminada", "Aprobada"),
            ("rechazada", "Rechazada"),
        ]

    def clean(self):
        cleaned = super().clean()
        estado = cleaned.get("estado_proceso")
        motivo = cleaned.get("motivo_rechazo")
        if estado == "rechazada" and not motivo:
            self.add_error("motivo_rechazo", "Debe indicar un motivo de rechazo.")
        return cleaned


class EmisorForm(forms.ModelForm):
    contadores = forms.ModelMultipleChoiceField(
        queryset=Contador.objects.all(),
        required=True,
        widget=forms.SelectMultiple(attrs={"size": 6}),
        label="Contadores",
        help_text="Seleccione al menos un contador responsable.",
    )
    rol_relacion = forms.ChoiceField(
        choices=[
            ("principal", "Principal"),
            ("suplente", "Suplente"),
            ("revisor", "Revisor"),
        ],
        initial="principal",
        required=True,
        label="Rol del contador",
    )

    class Meta:
        model = Emisor
        fields = ["nombre", "rut", "tipo_emisor", "estado", "contadores", "rol_relacion"]

    def clean_contadores(self):
        contadores = self.cleaned_data.get("contadores")
        if not contadores:
            raise forms.ValidationError("Debe asignar al menos un contador responsable al emisor.")
        return contadores

    def save(self, commit=True):
        emisor = super().save(commit=commit)
        if not commit:
            return emisor

        contadores = self.cleaned_data.get("contadores") or []
        rol_relacion = self.cleaned_data.get("rol_relacion") or "principal"
        for contador in contadores:
            EmisorContador.objects.update_or_create(
                emisor=emisor,
                contador=contador,
                rol_relacion=rol_relacion,
                defaults={"fecha_inicio": date.today()},
            )
        return emisor


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    rol = forms.ModelChoiceField(queryset=None, required=False, label="Rol")

    class Meta:
        model = Usuario
        fields = ["username", "email", "password", "nombre", "apellido", "estado"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rol"].queryset = Rol.objects.all()
        if self.instance.pk:
            # Pre-populate role if exists
            try:
                usuario_rol = UsuarioRol.objects.filter(usuario=self.instance).first()
                if usuario_rol:
                    self.fields["rol"].initial = usuario_rol.rol
            except Exception:
                pass
        else:
            self.fields["password"].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            import hashlib
            user.password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        
        if commit:
            user.save()
            # Handle Role
            rol = self.cleaned_data.get("rol")
            if rol:
                UsuarioRol.objects.update_or_create(
                    usuario=user,
                    defaults={"rol": rol}
                )
        return user


class EmisorContadorForm(forms.ModelForm):
    class Meta:
        model = EmisorContador
        fields = ["contador", "rol_relacion", "fecha_inicio", "fecha_fin"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.emisor = kwargs.pop("emisor", None)
        super().__init__(*args, **kwargs)
        if self.emisor:
            # Exclude accountants already assigned to this emisor to avoid duplicates
            assigned_ids = EmisorContador.objects.filter(emisor=self.emisor).values_list("contador_id", flat=True)
            self.fields["contador"].queryset = Contador.objects.exclude(id__in=assigned_ids).order_by("nombre_completo")


class EmisorUsuarioForm(forms.ModelForm):
    class Meta:
        model = EmisorUsuario
        fields = ["usuario", "rol_emisor"]

    def __init__(self, *args, **kwargs):
        self.emisor = kwargs.pop("emisor", None)
        super().__init__(*args, **kwargs)
        if self.emisor:
            assigned_ids = EmisorUsuario.objects.filter(emisor=self.emisor).values_list("usuario_id", flat=True)
            self.fields["usuario"].queryset = Usuario.objects.exclude(id__in=assigned_ids).order_by("username")


class RegistroUsuarioForm(forms.ModelForm):
    nombre = forms.CharField(max_length=100, required=True, label="Nombre")
    apellido = forms.CharField(max_length=100, required=True, label="Apellido")
    email = forms.EmailField(max_length=100, required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label="Repetir contraseña")
    tipo_cuenta = forms.ChoiceField(
        choices=[("accionista", "Accionista"), ("inversionista", "Inversionista")],
        required=True,
        widget=forms.RadioSelect,
        label="Tipo de cuenta"
    )
    emisores = forms.ModelMultipleChoiceField(
        queryset=Emisor.objects.filter(estado="activo").order_by("nombre"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        label="Emisores (Solo Accionistas)",
        help_text="Use Ctrl + Click para seleccionar múltiples."
    )

    class Meta:
        model = Usuario
        fields = ["nombre", "apellido", "email", "username", "password"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está ocupado.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        tipo_cuenta = cleaned_data.get("tipo_cuenta")
        emisores = cleaned_data.get("emisores")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Las contraseñas no coinciden.")

        if tipo_cuenta == "accionista":
            if not emisores:
                self.add_error("emisores", "Debe seleccionar al menos un emisor para crear una cuenta de Accionista.")
        
        return cleaned_data
