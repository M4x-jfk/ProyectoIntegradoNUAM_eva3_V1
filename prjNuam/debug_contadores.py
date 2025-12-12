import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prjNuam.settings')
django.setup()

from appNuam.models import Usuario, Rol, Contador

def debug_check():
    print("--- DEBUG CONTADORES ---")
    
    # 1. Check existing Contadores
    contadores = Contador.objects.all()
    print(f"Total Contadores in table: {contadores.count()}")
    for c in contadores:
        print(f" - {c.nombre_completo} (User ID: {c.usuario_id})")

    # 2. Check Users with Role CONTADOR or ANALISTA
    roles = Rol.objects.filter(nombre__in=["CONTADOR", "ANALISTA"])
    for r in roles:
        users = r.usuarios.all()
        print(f"\nUsers with role {r.nombre}: {users.count()}")
        for u in users:
            print(f" - {u.username} (ID: {u.id})")
            # Check if linked
            linked = Contador.objects.filter(usuario=u).exists()
            print(f"   -> Has Linked Contador Profile: {linked}")

if __name__ == "__main__":
    debug_check()
