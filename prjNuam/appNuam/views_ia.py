from django.shortcuts import render
from django.utils import timezone
import datetime

# Vistas para IA y Archivos Fuente

def ia_archivos_fuente_upload(request):
    context = {
        'mensaje': None
    }
    if request.method == 'POST':
        context['mensaje'] = "Archivo subido y enviado a procesar correctamente (Simulación)."
    return render(request, 'ia_automation/ia_archivos_fuente_upload.html', context)

def ia_archivos_fuente_list(request):
    # Datos dummy para simular la DB
    archivos = [
        {
            'id_archivo_fuente': 101,
            'nombre_original': 'calificaciones_2023_Q1.xlsx',
            'tipo_mime': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'subido_por': 'max',
            'fecha_subida': timezone.now() - datetime.timedelta(days=2),
            'estado_proceso': 'procesado',
            'extraido_por_ia': True,
            'ruta_archivo': '/media/uploads/calificaciones_2023_Q1.xlsx'
        },
        {
            'id_archivo_fuente': 102,
            'nombre_original': 'reporte_mensual_oct.pdf',
            'tipo_mime': 'application/pdf',
            'subido_por': 'admin',
            'fecha_subida': timezone.now() - datetime.timedelta(hours=4),
            'estado_proceso': 'en_proceso',
            'extraido_por_ia': True,
            'ruta_archivo': '/media/uploads/reporte_mensual_oct.pdf'
        },
        {
            'id_archivo_fuente': 103,
            'nombre_original': 'data_raw_bancos.csv',
            'tipo_mime': 'text/csv',
            'subido_por': 'sistema',
            'fecha_subida': timezone.now(),
            'estado_proceso': 'pendiente',
            'extraido_por_ia': False,
            'ruta_archivo': '/media/uploads/data_raw_bancos.csv'
        }
    ]
    return render(request, 'ia_automation/ia_archivos_fuente_list.html', {'archivos': archivos})

def ia_archivos_fuente_detail(request, pk):
    # Simulación de un archivo específico
    archivo = {
        'id_archivo_fuente': pk,
        'nombre_original': 'calificaciones_2023_Q1.xlsx',
        'fecha_subida': timezone.now() - datetime.timedelta(days=2),
        'subido_por': 'max',
        'estado_proceso': 'procesado',
        'ruta_archivo': '/media/uploads/calificaciones_2023_Q1.xlsx'
    }
    
    estructuras = [
        {
            'tipo_estructura': 'Tabla de Calificaciones',
            'confianza': 98,
            'fecha_detectado': timezone.now() - datetime.timedelta(days=2, hours=1),
            'datos_json': {'filas': 150, 'columnas': ['Emisor', 'Rating', 'Fecha']}
        },
        {
            'tipo_estructura': 'Metadatos del Documento',
            'confianza': 99,
            'fecha_detectado': timezone.now() - datetime.timedelta(days=2, hours=1),
            'datos_json': {'autor': 'Agencia X', 'fecha_creacion': '2023-01-15'}
        }
    ]
    
    return render(request, 'ia_automation/ia_archivos_fuente_detail.html', {
        'archivo': archivo,
        'estructuras': estructuras
    })

# Vistas para Archivos Normalizados y Validación

def ia_archivos_normalizados_list(request):
    archivos_normalizados = [
        {
            'id_archivo_normalizado': 501,
            'id_archivo_fuente': {'id_archivo_fuente': 101, 'nombre_original': 'calificaciones_2023_Q1.xlsx'},
            'formato': 'Excel Estándar NUAM',
            'fecha_generacion': timezone.now() - datetime.timedelta(days=1),
            'estado_validacion': 'validado'
        },
        {
            'id_archivo_normalizado': 502,
            'id_archivo_fuente': {'id_archivo_fuente': 102, 'nombre_original': 'reporte_mensual_oct.pdf'},
            'formato': 'Excel Estándar NUAM',
            'fecha_generacion': timezone.now() - datetime.timedelta(hours=2),
            'estado_validacion': 'con_errores'
        }
    ]
    return render(request, 'ia_automation/ia_archivos_normalizados_list.html', {'archivos_normalizados': archivos_normalizados})

def ia_validacion_archivo(request, pk):
    archivo = {
        'id_archivo_normalizado': pk,
        'id_archivo_fuente': {'nombre_original': 'reporte_mensual_oct.pdf'},
        'formato': 'Excel Estándar NUAM',
        'fecha_generacion': timezone.now() - datetime.timedelta(hours=2),
        'estado_validacion': 'con_errores'
    }
    
    errores = [
        {'fila': 12, 'campo': 'RUT Emisor', 'valor_detectado': '12.345.678-K', 'error': 'Formato inválido, falta guión'},
        {'fila': 45, 'campo': 'Fecha Clasificación', 'valor_detectado': '30/02/2023', 'error': 'Fecha no existe'},
        {'fila': 46, 'campo': 'Monto', 'valor_detectado': 'N/A', 'error': 'El campo monto es obligatorio'}
    ]
    
    # Si el ID es 501 (validado), mandamos lista vacía de errores
    if str(pk) == '501':
        archivo['estado_validacion'] = 'validado'
        errores = []

    return render(request, 'ia_automation/ia_validacion_archivo.html', {
        'archivo': archivo,
        'errores': errores
    })

# Vistas para Carga Masiva y Trazabilidad

def ia_carga_masiva_resumen(request, pk):
    carga = {
        'id_carga': pk,
        'estado': 'parcial', # completa, parcial, error
        'fecha_inicio': timezone.now() - datetime.timedelta(minutes=30),
        'fecha_fin': timezone.now(),
        'total_filas': 150,
        'filas_ok': 148,
        'filas_error': 2
    }
    
    detalles = [
        {'nro_fila': 12, 'estado': 'rechazada', 'mensaje_error': 'RUT Emisor inválido', 'id_calificacion_afectada': None},
        {'nro_fila': 45, 'estado': 'rechazada', 'mensaje_error': 'Fecha inválida', 'id_calificacion_afectada': None},
        {'nro_fila': 1, 'estado': 'insertada', 'mensaje_error': None, 'id_calificacion_afectada': 1001},
        {'nro_fila': 2, 'estado': 'actualizada', 'mensaje_error': None, 'id_calificacion_afectada': 1002},
    ]
    
    return render(request, 'ia_automation/ia_carga_masiva_resumen.html', {
        'carga': carga,
        'detalles': detalles
    })

def ia_trazabilidad(request):
    # Datos dummy para la vista inicial o un resultado de búsqueda
    context = {}
    # Simulamos que se buscó algo si hay parámetros o por defecto mostramos uno
    context['archivo_fuente'] = {
        'id_archivo_fuente': 101,
        'nombre_original': 'calificaciones_2023_Q1.xlsx',
        'fecha_subida': timezone.now() - datetime.timedelta(days=5),
        'estado_proceso': 'procesado'
    }
    context['tarea_ia'] = {
        'id_tarea_ia': 701,
        'modelo_utilizado': 'GPT-4-Turbo',
    }
    context['estructuras_count'] = 3
    context['archivo_normalizado'] = {
        'id_archivo_normalizado': 501,
        'estado_validacion': 'validado'
    }
    context['carga_masiva'] = {
        'id_carga': 88,
        'fecha_inicio': timezone.now() - datetime.timedelta(days=4),
        'total_filas': 150,
        'filas_ok': 150,
        'filas_error': 0
    }
    context['calificaciones_afectadas'] = [
        {'id': 1001, 'estado': 'Vigente'},
        {'id': 1002, 'estado': 'Vigente'},
        {'id': 1003, 'estado': 'Vigente'},
        {'id': 1004, 'estado': 'Vigente'},
        {'id': 1005, 'estado': 'Vigente'},
        {'id': 1006, 'estado': 'Vigente'},
    ]
    
    return render(request, 'ia_automation/ia_trazabilidad.html', context)

# Vistas para Power BI

def powerbi_dashboard_general(request):
    return render(request, 'ia_automation/powerbi_dashboard_general.html')

def powerbi_dashboard_ejecutivo(request):
    return render(request, 'ia_automation/powerbi_dashboard_ejecutivo.html')
