import hashlib
from django.contrib.auth.backends import BaseBackend
from .models import Usuario

class SHA256Backend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        try:
            # Buscar usuario por correo (username)
            user = Usuario.objects.get(correo=username)
            
            # Verificar estado
            if user.estado != Usuario.Estado.ACTIVO:
                return None
            
            # Verificar contraseña (SHA-256)
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            if user.hash_password == password_hash:
                return user
            
        except Usuario.DoesNotExist:
            return None
            
        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
