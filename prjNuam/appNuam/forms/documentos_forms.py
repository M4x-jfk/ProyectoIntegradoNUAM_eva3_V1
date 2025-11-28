from django import forms
from appNuam.models import Documento


class DocumentoForm(forms.ModelForm):
    """HU13 subida básica alineada a la tabla documentos."""

    class Meta:
        model = Documento
        fields = ['tipo_documento', 'ruta_archivo', 'visibilidad', 'version']
