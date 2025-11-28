from appNuam.models import AuditoriaEvento, Usuario


def registrar_evento(actor: Usuario | None, accion: str, objeto: str | None = None, objeto_id=None, metadata=None):
    """HU06/HU10/HU20: helper generico."""
    return AuditoriaEvento.objects.create(
        actor=actor,
        accion=accion,
        objeto=objeto,
        objeto_id=str(objeto_id) if objeto_id else None,
        metadata=metadata or {},
    )
