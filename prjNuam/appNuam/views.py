from functools import wraps

from django.shortcuts import redirect, render

from .models import Usuario


def _login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('nuam_user'):
            return redirect('login')
        return view_func(request, *args, **kwargs)

    return wrapper


def login_view(request):
    error = None
    if request.session.get('nuam_user'):
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        usuario = Usuario.objects.filter(correo__iexact=email).first()
        if usuario:
            request.session['nuam_user'] = usuario.correo
            request.session['nuam_nombre'] = usuario.nombre or usuario.correo
            return redirect('dashboard')
        error = 'Usuario no encontrado. Use admin@nuam.cl o analista@nuam.cl.'

    return render(request, 'templatesApp/login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('login')


@_login_required
def dashboard_view(request):
    return render(request, 'templatesApp/dashboard.html')


@_login_required
def usuarios_view(request):
    return render(request, 'templatesApp/usuarios.html')


@_login_required
def partys_view(request):
    return render(request, 'templatesApp/partys.html')


@_login_required
def calificaciones_view(request):
    return render(request, 'templatesApp/calificaciones.html')


@_login_required
def carga_masiva_view(request):
    return render(request, 'templatesApp/carga_masiva.html')


@_login_required
def auditoria_view(request):
    return render(request, 'templatesApp/auditoria.html')
