from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .models import Usuario, Rol, Documento, ArchivoCarga, Calificacion, Reporte

# --- Login & Logout ---

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login manual para establecer la sesión
            # Nota: Como usamos un modelo personalizado no-Django auth completo, 
            # guardamos datos en sesión manualmente si authenticate devuelve el objeto Usuario.
            
            # Registrar último login
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            # Guardar en sesión
            request.session['user_id'] = user.pk
            request.session['user_name'] = user.nombre
            request.session['user_email'] = user.correo
            
            # Obtener roles
            roles = list(user.roles.values_list('nombre', flat=True))
            request.session['user_roles'] = roles
            
            # Redirección basada en rol
            if 'ADMIN_TI' in roles:
                return redirect('dashboard_admin')
            elif 'ANALISTA' in roles:
                return redirect('dashboard_analista')
            elif 'SUPERVISOR' in roles:
                return redirect('dashboard_supervisor')
            elif 'ACCIONISTA' in roles:
                return redirect('dashboard_accionista')
            elif 'INVERSIONISTA' in roles:
                return redirect('dashboard_inversionista')
            else:
                # Rol por defecto o error
                return redirect('dashboard_analista')
        else:
            return render(request, 'templatesApp/login.html', {'error': 'Credenciales inválidas o cuenta inactiva.'})
            
    return render(request, 'templatesApp/login.html')

def logout_view(request):
    logout(request) # Limpia la sesión de Django
    request.session.flush() # Asegura limpieza total
    return redirect('login')

# --- Decorador personalizado simple ---
def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if 'user_id' not in request.session:
                return redirect('login')
            
            user_roles = request.session.get('user_roles', [])
            if any(role in allowed_roles for role in user_roles):
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'ia_automation/base_ia.html', {'error': 'No tiene permisos para acceder a esta vista.'}) # O 403
        return _wrapped_view
    return decorator

# --- Dashboards ---

@role_required(['ADMIN_TI'])
def dashboard_admin_view(request):
    # Datos reales de BD
    usuarios_count = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(estado=Usuario.Estado.ACTIVO).count()
    roles_count = Rol.objects.count()
    
    # Auditoría reciente (simulada con created_at de documentos por ahora, o historial si hubiera)
    ultimos_docs = Documento.objects.order_by('-created_at')[:5]
    
    context = {
        'usuarios_count': usuarios_count,
        'usuarios_activos': usuarios_activos,
        'roles_count': roles_count,
        'ultimos_docs': ultimos_docs,
        'user_name': request.session.get('user_name')
    }
    return render(request, 'templatesApp/dashboard_admin.html', context)

@role_required(['ANALISTA'])
def dashboard_analista_view(request):
    # Tareas pendientes (ej: cargas en proceso o fallidas)
    cargas_pendientes = ArchivoCarga.objects.filter(estado=ArchivoCarga.Estado.EN_PROCESO).count()
    cargas_fallidas = ArchivoCarga.objects.filter(estado=ArchivoCarga.Estado.FALLIDA).count()
    
    # Mis documentos recientes
    mis_docs = Documento.objects.filter(created_by_id=request.session['user_id']).order_by('-created_at')[:5]
    
    context = {
        'cargas_pendientes': cargas_pendientes,
        'cargas_fallidas': cargas_fallidas,
        'mis_docs': mis_docs,
        'user_name': request.session.get('user_name')
    }
    return render(request, 'templatesApp/dashboard_analista.html', context)

@role_required(['SUPERVISOR'])
def dashboard_supervisor_view(request):
    # Calificaciones pendientes de aprobación
    calificaciones_pendientes = Calificacion.objects.filter(estado=Calificacion.Estado.PENDIENTE_APROBACION).count()
    
    # Resumen de cargas del día
    hoy = timezone.now().date()
    cargas_hoy = ArchivoCarga.objects.filter(created_at__date=hoy).count()
    
    context = {
        'calificaciones_pendientes': calificaciones_pendientes,
        'cargas_hoy': cargas_hoy,
        'user_name': request.session.get('user_name')
    }
    return render(request, 'templatesApp/dashboard_supervisor.html', context)

@role_required(['ACCIONISTA'])
def dashboard_accionista_view(request):
    # KPIs de alto nivel
    total_calificaciones_vigentes = Calificacion.objects.filter(estado=Calificacion.Estado.VIGENTE).count()
    monto_total_vigente = 0 # Se podría sumar con aggregate
    
    # Power BI URL (placeholder)
    powerbi_url = "https://app.powerbi.com/reportEmbed?reportId=..."
    
    context = {
        'total_calificaciones': total_calificaciones_vigentes,
        'powerbi_url': powerbi_url,
        'user_name': request.session.get('user_name')
    }
    return render(request, 'templatesApp/dashboard_accionista.html', context)

@role_required(['INVERSIONISTA'])
def dashboard_inversionista_view(request):
    # Similar a accionista pero quizás con otra vista
    total_calificaciones_vigentes = Calificacion.objects.filter(estado=Calificacion.Estado.VIGENTE).count()
    powerbi_url = "https://app.powerbi.com/reportEmbed?reportId=..."
    
    context = {
        'total_calificaciones': total_calificaciones_vigentes,
        'powerbi_url': powerbi_url,
        'user_name': request.session.get('user_name')
    }
    return render(request, 'templatesApp/dashboard_inversionista.html', context)

# --- Vistas Placeholder (existentes) ---
def usuarios_view(request): return render(request, 'ia_automation/base_ia.html')
def partys_view(request): return render(request, 'ia_automation/base_ia.html')
def calificaciones_view(request): return render(request, 'ia_automation/base_ia.html')
def carga_masiva_view(request): return render(request, 'ia_automation/base_ia.html')
def auditoria_view(request): return render(request, 'ia_automation/base_ia.html')
def reportes_view(request): return render(request, 'ia_automation/base_ia.html')
def configuracion_view(request): return render(request, 'ia_automation/base_ia.html')
def perfil_view(request): return render(request, 'ia_automation/base_ia.html')
def dashboard_view(request): return redirect('login') # Redirigir al login si intentan entrar directo
