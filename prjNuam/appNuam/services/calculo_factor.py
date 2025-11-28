from decimal import Decimal
from appNuam.models import Calificacion


def calcular_factor(calificacion: Calificacion) -> Decimal:
    """
    HU19: calculo centralizado del factor.
    Placeholder: factor = monto * 0.05, puede usar parametros en futuras versiones.
    """
    monto = calificacion.monto or Decimal('0')
    return monto * Decimal('0.05')
