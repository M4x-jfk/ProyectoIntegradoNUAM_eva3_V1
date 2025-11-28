from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Correo', max_length=255)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if len(pwd) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return pwd
