from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_initial_accounts(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Usuario = apps.get_model('appNuam', 'Usuario')
    Rol = apps.get_model('appNuam', 'Rol')
    UsuarioRol = apps.get_model('appNuam', 'UsuarioRol')

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@nuam.cl',
            password='Nuam#2025',
            first_name='Administrador',
            last_name='NUAM',
        )

    rol_admin, _ = Rol.objects.get_or_create(
        nombre='Administrador',
        defaults={'descripcion': 'Rol con todos los permisos del mantenedor tributario.'},
    )

    usuario_admin, created = Usuario.objects.get_or_create(
        correo='admin@nuam.cl',
        defaults={
            'nombre': 'Administrador NUAM',
            'hash_password': make_password('Nuam#2025'),
        },
    )
    if created:
        UsuarioRol.objects.create(usuario=usuario_admin, rol=rol_admin)

    rol_analista, _ = Rol.objects.get_or_create(nombre='Analista', defaults={'descripcion': 'Analista tributario'})
    usuario_analista, created = Usuario.objects.get_or_create(
        correo='analista@nuam.cl',
        defaults={
            'nombre': 'Analista Tributario',
            'hash_password': make_password('Analista#2025'),
        },
    )
    if created:
        UsuarioRol.objects.create(usuario=usuario_analista, rol=rol_analista)


def remove_initial_accounts(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Usuario = apps.get_model('appNuam', 'Usuario')

    User.objects.filter(username='admin', email='admin@nuam.cl').delete()
    Usuario.objects.filter(correo__in=['admin@nuam.cl', 'analista@nuam.cl']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('appNuam', '0002_adjust_usuario_roles_pk'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_initial_accounts, remove_initial_accounts),
    ]
