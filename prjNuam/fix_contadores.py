import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prjNuam.settings')
django.setup()

from appNuam.models import Usuario, Rol, Contador

def fix_contadores():
    print("--- FIXING MISSING CONTADORES ---")
    
    roles = Rol.objects.filter(nombre__in=["CONTADOR", "ANALISTA"])
    count = 0
    for r in roles:
        users = r.usuarios.all()
        for u in users:
            # Check if exists
            if not Contador.objects.filter(usuario=u).exists():
                print(f"Creating Contador profile for {u.username} ({r.nombre})...")
                full_name = u.full_name or u.username
                Contador.objects.create(
                    usuario=u,
                    nombre_completo=full_name,
                    email=u.email
                )
                count += 1
            else:
                print(f"Contador profile already exists for {u.username}")

    print(f"\nDone. Created {count} missing profiles.")

if __name__ == "__main__":
    fix_contadores()
