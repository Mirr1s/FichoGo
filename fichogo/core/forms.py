from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class EstudianteRegistroForm(UserCreationForm):
    username = forms.CharField(label='Código de estudiante', max_length=30)
    first_name = forms.CharField(label='Nombre', max_length=30)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este código de estudiante ya está registrado.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user