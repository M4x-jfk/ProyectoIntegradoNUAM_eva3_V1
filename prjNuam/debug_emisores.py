import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prjNuam.settings')
django.setup()

from appNuam.models import Usuario, Emisor, EmisorUsuario, Rol, Accionista

def debug_check():
    print("--- DEBUG CHECK ---")
    
    # 1. Check Active Emisores
    emisores = Emisor.objects.filter(estado="activo")
    print(f"Active Emisores Count: {emisores.count()}")
    for e in emisores:
        print(f" - {e.nombre} (ID: {e.id})")

    # 2. Check Last Created User
    last_user = Usuario.objects.order_by('-fecha_creacion').first()
    if not last_user:
        print("No users found.")
        return

    print(f"\nLast User: {last_user.username} (ID: {last_user.id})")
    
    # 3. Check Role
    roles = last_user.roles.all()
    print(f"Roles: {[r.nombre for r in roles]}")

    # 4. Check EmisorUsuario
    relations = EmisorUsuario.objects.filter(usuario=last_user)
    print(f"EmisorUsuario relations found: {relations.count()}")
    for rel in relations:
        print(f" - Emisor: {rel.emisor.nombre}, Rol: {rel.rol_emisor}")

if __name__ == "__main__":
    debug_check()
