# Version: 1.0
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django import forms
from django.conf import settings


class CustomUser(AbstractUser):

    email = models.EmailField(unique=True)
    di_tipo = models.CharField(max_length=20)
    di= models.CharField(max_length=20,default='00000000000')#Default para las que yo ya tengo agg, pero no es necesario si los datos son obligatorios
    nacimiento = models.DateField()
    sexo = models.CharField(max_length=10)
    genero = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    paisResidencia = models.CharField(max_length=50)
    carrera = models.CharField(max_length=100)
    
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="user",
    )

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'di_tipo','nacimiento','sexo','genero','telefono','paisResidencia']  # Reemplaza 'other_field' con tus otros campos
        app_label='SIGES'
#para el curriculum

class Curriculum(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    imagen_perfil = models.ImageField(upload_to='perfiles/')
    imagen_documento = models.ImageField(upload_to='documentos/')
    #Los campos de CustomUser
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    di_tipo = models.CharField(max_length=255)#tipo de documento de identidad
    nacimiento = models.DateField()
    sexo = models.CharField(max_length=255)
    genero = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255)
    paisResidencia = models.CharField(max_length=255)
    di = models.CharField(max_length=255)#Dcoumento de identidad
    carrera = models.CharField(max_length=255)

class Solicitud(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre_empresa = models.CharField(max_length=255)
    cargo_aspirado = models.CharField(max_length=255)
    direccion_empresa = models.CharField(max_length=255)
    sueldo = models.CharField(max_length=255)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
