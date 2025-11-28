import hashlib
from django import forms
from appNuam.models import Usuario, Rol


class UsuarioForm(forms.ModelForm):
    """HU09: gestión usuarios/roles."""

    password = forms.CharField(
        label='Contraseña (SHA-256)',
        widget=forms.PasswordInput,
        required=False,
        help_text='Déjalo vacío para mantener la actual.',
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Rol.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nombre', 'apellido', 'estado', 'roles', 'password']

    def save(self, commit=True):
        instance = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            instance.password_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        if commit:
            instance.save()
            self.save_m2m()
        return instance
