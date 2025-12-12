import os
import django
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prjNuam.settings')
django.setup()

from appNuam.models import Usuario

def run():
    # Update all users to have password '1234'
    default_pass = "1234"
    pass_hash = hashlib.sha256(default_pass.encode("utf-8")).hexdigest()
    
    print("Updating existing users...")
    users = Usuario.objects.all()
    count = 0
    for user in users:
        user.password_hash = pass_hash
        user.save()
        count += 1
    
    print(f"Updated {count} users with default password '{default_pass}'.")

if __name__ == "__main__":
    run()
