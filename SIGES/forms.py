from django import forms
from .models import CustomUser, Curriculum
from django.core.validators import RegexValidator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError



class UsuarioFrom(forms.ModelForm):
    di=forms.CharField(validators=[RegexValidator(r'^\d+$','Ingrese solo numeros')])
    class Meta:
        model=CustomUser
        fields=[
                'first_name',#nombre
                'last_name',#apellido
                'email',#correo ES UNICO
                'di_tipo',#tipo de documento de identidad
                'di',#documento de identidad
                'nacimiento',#fecha de nacimiento
                'sexo',
                'genero'
                ,'telefono'
                ,'paisResidencia'#pais de residencia
                ,'carrera'
                ,'password']
    def save(self, commit=True):
        user = super(UsuarioFrom, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        base_username = f"{self.cleaned_data['first_name']}{self.cleaned_data['last_name']}"
        user.username = base_username
        counter = 1
        while CustomUser.objects.filter(username=user.username).exists():
            user.username = f"{base_username}{counter}"
            counter += 1
        if commit:
            user.save()
        return user
## formulario para el login 
#usaremos el que proporciona django

class EmailAuthenticationForm(AuthenticationForm):
    username = None  # No utilizamos el campo username
    email = forms.EmailField(label='Correo electrónico', required=True, max_length=254)
    
    
    def __init__(self, request=None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise ValidationError(
                    "Por favor, introduce una dirección de correo electrónico y una contraseña correctos. "
                    "Ten en cuenta que ambos campos distinguen entre mayúsculas y minúsculas."
                )
            elif not self.user_cache.is_active:
                raise ValidationError("Esta cuenta está inactiva.")
        return self.cleaned_data

    def get_user(self):
        return self.user_cache
    
    ## formulario de Creacion de estudiante.
class EstudianteForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=[
                'first_name',#nombre
                'last_name',#apellido
                'email',#correo ES UNICO
                'di_tipo',#tipo de documento de identidad
                'di',#documento de identidad
                'nacimiento',#fecha de nacimiento
                'sexo',
                'genero'
                ,'telefono'
                ,'paisResidencia'#pais de residencia
                ,'carrera'
                ,'password']
    def save(self, commit=True):
        user = super(EstudianteForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        base_username = f"{self.cleaned_data['first_name']}{self.cleaned_data['last_name']}"
        user.username = base_username
        counter = 1
        while CustomUser.objects.filter(username=user.username).exists():
            user.username = f"{base_username}{counter}"
            counter += 1
        if commit:
            user.save()
        return user
    
class CurriculumForm(forms.ModelForm):
    imagen_perfil = forms.ImageField(required=False)
    imagen_documento = forms.ImageField(required=False)
    direccion = forms.CharField(max_length=255, required=False)
    class Meta:
        model=Curriculum
        fields=[
                'first_name',#nombre
                'last_name',#apellido
                'email',#correo ES UNICO
                'di_tipo',#tipo de documento de identidad
                'di',#documento de identidad
                'nacimiento',#fecha de nacimiento
                'sexo',
                'genero'
                ,'telefono'
                ,'paisResidencia',#pais de residencia
                'imagen_perfil',
                'imagen_documento',
                'direccion',
                'carrera'
            ] 