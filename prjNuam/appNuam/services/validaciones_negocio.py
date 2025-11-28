from appNuam.models import Calificacion


def validar_calificacion(calificacion: Calificacion) -> list[str]:
    """
    HU18: validaciones de negocio.
    Devuelve lista de errores; vacia si todo OK.
    """
    errores: list[str] = []
    if calificacion.monto is None or calificacion.monto <= 0:
        errores.append('El monto debe ser mayor a cero.')
    if not calificacion.emisor_id:
        errores.append('Toda calificación debe asociarse a un emisor.')
    return errores
