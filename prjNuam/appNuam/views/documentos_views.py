from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, View

from appNuam.forms.documentos_forms import DocumentoForm
from appNuam.models import Documento, InformeOficial
from appNuam.services.documentos_service import registrar_documento, registrar_descarga_informe
from appNuam.services.auditoria_service import registrar_evento
from .seguridad_views import RoleRequiredMixin


class DocumentoListView(RoleRequiredMixin, ListView):
    """HU13: listado documentos."""

    model = Documento
    template_name = 'templatesApp/documentos/listado.html'
    context_object_name = 'documentos'
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']


class DocumentoDetailView(RoleRequiredMixin, DetailView):
    model = Documento
    template_name = 'templatesApp/documentos/detalle.html'
    context_object_name = 'documento'
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']


class DocumentoUploadView(RoleRequiredMixin, CreateView):
    """HU13: subida simple (sin carga masiva)."""

    model = Documento
    form_class = DocumentoForm
    template_name = 'templatesApp/documentos/subir.html'
    success_url = reverse_lazy('documentos_list')
    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI']

    def form_valid(self, form):
        doc = form.save(commit=False)
        doc.created_by = self.request.user
        doc = registrar_documento(doc)
        registrar_evento(self.request.user, 'DOCUMENTO_SUBIR', objeto='Documento', objeto_id=doc.pk)
        return super().form_valid(form)


class InformeOficialDownloadView(RoleRequiredMixin, View):
    """HU17: descarga con registro auditoria (placeholder)."""

    allowed_roles = ['ANALISTA', 'SUPERVISOR', 'ADMIN_TI', 'ACCIONISTA', 'INVERSIONISTA']

    def get(self, request, *args, **kwargs):
        informe = InformeOficial.objects.filter(pk=kwargs['pk']).select_related('documento').first()
        if not informe:
            messages.error(request, 'Informe no encontrado.')
            return redirect('documentos_list')

        registrar_descarga_informe(request.user, informe)
        # Placeholder: en entorno real se haria FileResponse.
        registrar_evento(request.user, 'INFORME_DESCARGAR', objeto='InformeOficial', objeto_id=informe.pk)
        messages.info(request, 'Descarga de informe registrada (placeholder).')
        return redirect('documentos_list')
