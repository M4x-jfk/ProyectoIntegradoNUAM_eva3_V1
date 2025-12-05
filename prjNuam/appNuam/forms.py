from datetime import date

from django import forms

from .models import CalificacionTributaria, Instrumento


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

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario", None)
        self.emisores_permitidos = kwargs.pop("emisores_permitidos", None)
        super().__init__(*args, **kwargs)
        if self.emisores_permitidos is not None:
            self.fields["emisor"].queryset = self.emisores_permitidos
        self.fields["instrumento"].queryset = Instrumento.objects.none()
        if "emisor" in self.data:
            try:
                emisor_id = int(self.data.get("emisor"))
                self.fields["instrumento"].queryset = Instrumento.objects.filter(emisor_id=emisor_id)
            except (TypeError, ValueError):
                pass
        elif self.instance and self.instance.pk:
            self.fields["instrumento"].queryset = Instrumento.objects.filter(emisor=self.instance.emisor)

    def clean_anio(self):
        anio = self.cleaned_data.get("anio")
        current_year = date.today().year
        if anio is None or anio < 2023 or anio > current_year:
            raise forms.ValidationError("El año de la calificación debe estar entre 2023 y el año actual.")
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

        return cleaned
