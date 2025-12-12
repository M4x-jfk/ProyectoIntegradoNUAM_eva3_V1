from .models import Usuario

class SHA256Backend(BaseBackend):
    """
    Backend placeholder que compara hash SHA-256 plano en password_hash.
    Sustituye con lógica real/segura (ideal: Django auth).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Force usage of appNuam.Usuario
        User = Usuario
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        # Si el modelo no expone password_hash, no autenticamos y dejamos a ModelBackend.
        expected = getattr(user, "password_hash", None)
        if expected:
            import hashlib

            candidate = hashlib.sha256(password.encode("utf-8")).hexdigest()
            if expected == candidate:
                return user
        return None

    def get_user(self, user_id):
        User = Usuario
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# Alias para compatibilidad si se configuró DummyBackend
DummyBackend = SHA256Backend
