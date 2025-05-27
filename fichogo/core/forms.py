from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

class EstudianteRegistroForm(UserCreationForm):
    username = forms.CharField(label='Código de estudiante', max_length=30, error_messages={
        'unique': _('Este código de estudiante ya está registrado.'),
        'required': _('El código de estudiante es obligatorio.'),
    })
    first_name = forms.CharField(label='Nombre', max_length=30, error_messages={
        'required': _('El nombre es obligatorio.'),
    })
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, error_messages={
        'required': _('La contraseña es obligatoria.'),
    })
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput, error_messages={
        'required': _('Debes confirmar la contraseña.'),
    })

    class Meta:
        model = User
        fields = ['username', 'first_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Este código de estudiante ya está registrado.'))
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Las contraseñas no coinciden.'))
        if password1 and len(password1) < 8:
            raise forms.ValidationError(_('La contraseña debe tener al menos 8 caracteres.'))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user