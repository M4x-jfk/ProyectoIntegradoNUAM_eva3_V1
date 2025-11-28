from appNuam.models import ParametroSistema


def obtener_parametro(clave: str) -> ParametroSistema | None:
    return ParametroSistema.objects.filter(clave=clave).order_by('-version').first()


def actualizar_parametro(data: dict) -> ParametroSistema:
    last = ParametroSistema.objects.filter(clave=data.get('clave')).order_by('-version').first()
    version = (last.version + 1) if last else 1
    param = ParametroSistema.objects.create(
        clave=data.get('clave'),
        valor=data.get('valor'),
        tipo=data.get('tipo', 'str'),
        descripcion=data.get('descripcion'),
        version=version,
    )
    return param
