from appNuam.models import Documento, InformeOficial, Usuario


def registrar_documento(doc: Documento) -> Documento:
    """HU13: guarda documento y aumenta version."""
    last_version = (
        Documento.objects.filter(filename=doc.filename, created_by=doc.created_by)
        .order_by('-version')
        .first()
    )
    doc.version = (last_version.version + 1) if last_version else 1
    doc.save()
    return doc


def registrar_descarga_informe(usuario: Usuario, informe: InformeOficial):
    """HU17: solo registrar evento de descarga (placeholder)."""
    informe.descripcion = informe.descripcion or 'Descarga informe'
    informe.save(update_fields=['descripcion'])
    # En un sistema completo se anotaría en auditoría; se delega a registrar_evento desde vista.
    return informe
