from django import forms
from appNuam.models import Calificacion, Aprobacion, ParametroSistema


class CalificacionForm(forms.ModelForm):
    """HU01-HU03 + HU19."""

    class Meta:
        model = Calificacion
        fields = [
            'emisor',
            'instrumento',
            'anio',
            'monto',
            'factor',
            'rating',
            'estado_registro',
            'origen',
        ]
        widgets = {
            'anio': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
        }


class AprobacionForm(forms.ModelForm):
    """HU14."""

    class Meta:
        model = Aprobacion
        fields = ['estado', 'motivo']


class ParametroSistemaForm(forms.ModelForm):
    """HU16/HU19."""

    class Meta:
        model = ParametroSistema
        fields = ['clave', 'valor', 'tipo', 'descripcion']
