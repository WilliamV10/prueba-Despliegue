from django.shortcuts import render, redirect
from .forms import UsuarioFrom
from django.contrib import messages
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import EmailAuthenticationForm
from django.conf import settings
from rolepermissions.decorators import has_role_decorator
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_role
from .roles import Admin, Estudiante
from rolepermissions.roles import get_user_roles
from .models import CustomUser, Curriculum
from .forms import EstudianteForm,CurriculumForm
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.core import serializers


# Create your views here.

def registrar(request):
    min_fecha = date.today() - timedelta(days=18*365)
    if request.method=='POST':
        print(request.POST)
        form=UsuarioFrom(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #Para cambiar los valores de ID por el texto
            user.sexo = request.POST.get('sexo_texto')
            user.genero = request.POST.get('genero_texto')
            user.paisResidencia = request.POST.get('pais_texto')
            user.carrera = request.POST.get('carrera_texto')
            user.save()
            #mensaje para avisar que se guardo
            messages.success(request,'Usuario Registrado Correctamente')
            curriculum = create_curriculum_from_user(user)
            return redirect('login')
        else:
            messages.error(request,'Error al registrar el usuario')    
        
    else:
        form=UsuarioFrom()        
    return render(request,'autenticacion/register.html',{'form_registro':form,'min_fecha':min_fecha})

@login_required
def index (request):
    return render(request,'index.html')

#vista de login 
def login_view(request):
    print(settings.AUTH_USER_MODEL)
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        print(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is None:
                print("No se encontró ningún usuario con estas credenciales")
            else:
                login(request, user)
                if request.user.is_authenticated:  # Comprueba si el usuario está autenticado
                    print("El usuario está autenticado")

                    # Asigna el rol al usuario después de iniciar sesión
                    if user.is_superuser:
                        assign_role(user, Admin)
                        print("El usuario es un Admin")
                    else:
                        assign_role(user, Estudiante)
                        print("El usuario es un Estudiante")
                    
                    # Redirige a diferentes vistas basándote en el rol del usuario
                    if has_role(user, 'Admin'):
                        return redirect('index-admin')
                    else:
                        return redirect('index-estudiante')
                else:
                    print("El usuario no está autenticado")
        else:
            messages.error(request,"Email o contraseña incorrectos")  # Se imprime si form.is_valid() devuelve False
            print(form.errors) 
    else:
        form = EmailAuthenticationForm(request)
    return render(request, 'Autenticacion/login.html', {'form': form})

#Cerrar sesion
def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
@has_role_decorator(Admin)
def indexAdmin(request):
    q = request.GET.get('q')
    page_number = request.GET.get('page', 1)  # Obtiene el número de página de la solicitud

    # Filtra los estudiantes basándote en el término de búsqueda
    if q:
        estudiantes_list = CustomUser.objects.filter(
            Q(first_name__icontains=q) | 
            Q(last_name__icontains=q) | 
            Q(email__icontains=q)
        ).order_by('last_name')
    else:
        estudiantes_list = CustomUser.objects.all().order_by('last_name')

    # Crea un paginador
    paginator = Paginator(estudiantes_list, 5)  # Muestra 5 estudiantes por página

    # Obtiene los estudiantes de la página actual
    estudiantes = paginator.get_page(page_number)

    # Comprueba si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Serializa los objetos a JSON
        data = [{'id': estudiante.pk, 'first_name': estudiante.first_name, 'last_name': estudiante.last_name, 'email': estudiante.email,'username':estudiante.username,'sexo':estudiante.sexo, 'genero':estudiante.genero, 'telefono':estudiante.telefono, 'nacimiento':estudiante.nacimiento} for estudiante in estudiantes]
        # Devuelve los resultados de búsqueda como JSON
        return JsonResponse(data, safe=False)
    else:
        return render(request,'admin/index-admin.html',{'Estudiantes':estudiantes})
    
    
#Vistas de usuario
@login_required
@has_role_decorator(Estudiante)
def indexUser(request):
    curriculum = Curriculum.objects.get(user=request.user)
    return render(request,'estudiante/index-estudiante.html',{'curriculum_id':curriculum.id})

@login_required
@has_role_decorator(Estudiante)
def seguimiento(request):
    solicitudes_list = Solicitud.objects.filter(user=request.user)
    paginator = Paginator(solicitudes_list, 5)  # Muestra 5 solicitudes por página

    page_number = request.GET.get('page')
    solicitudes = paginator.get_page(page_number)

    return render(request, 'estudiante/solicitudes.html', {'solicitudes': solicitudes})

## COMENTARIOOOO
# Para agregar un nuevo rol: Iremos al archivo Roles.py.
# si una pagina, debe de ser vista por ambos, se debe de agregar en el decorador de ambas vistas
# como lo hacemos ? pues con @has_role_decorator(Admin,Estudiante)

#CRUD de Estudiantes
@login_required
@has_role_decorator(Admin)
def crearEstudiante(request):
    formulario = EstudianteForm(request.POST or None)
    if request.method=='POST':
        formulario = EstudianteForm(request.POST)
        if formulario.is_valid():
            user = formulario.save(commit=False)
         #Para cambiar los valores de ID por el texto
            user.sexo = request.POST.get('sexo_texto')
            user.genero = request.POST.get('genero_texto')
            user.paisResidencia = request.POST.get('pais_texto')
            user.carrera = request.POST.get('carrera_texto')
            formulario.save()
            return redirect('index-admin')
    else:
        formulario = EstudianteForm()
    return render(request,'admin/crearEstudiante.html',{'formulario':formulario})

@login_required
@has_role_decorator(Admin) 
def editarEstudiante(request, id):
    min_fecha = date.today() - timedelta(days=18*365)
    Estudiante=CustomUser.objects.get(id=id)
    formulario=EstudianteForm(request.POST or None, request.FILES or None,instance=Estudiante)
    if formulario.is_valid() and request.POST:
        user = formulario.save(commit=False)
         #Para cambiar los valores de ID por el texto
        user.sexo = request.POST.get('sexo_texto')
        user.genero = request.POST.get('genero_texto')
        user.paisResidencia = request.POST.get('pais_texto')
        user.carrera = request.POST.get('carrera_texto')
        user.save()
        return redirect('index-admin')
    
    return render(request,'admin/editarEstudiante.html',{'formulario':formulario,'min_fecha':min_fecha})

@login_required
@has_role_decorator(Admin)
def eliminarEstudiante(request, id):
    Estudiante = CustomUser.objects.get(id=id)
    Estudiante.delete()
    return redirect('index-admin')

def estudianteCurriculum(request):
    return render(request,'estudiante/curriculum.html')


#para copiar los datos de customuser a curriculum
def create_curriculum_from_user(user):
    curriculum = Curriculum.objects.create(
        user=user,
        direccion="",
        imagen_perfil=None,
        imagen_documento=None,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        di_tipo=user.di_tipo,
        nacimiento=user.nacimiento,
        sexo=user.sexo,
        genero=user.genero,
        telefono=user.telefono,
        paisResidencia=user.paisResidencia,
        di=user.di,
        carrera=user.carrera,
    )
    return curriculum


def crearCurriculum(request, id):
    min_fecha = date.today() - timedelta(days=18*365)
    user = CustomUser.objects.get(id=id)
    curriculum = Curriculum.objects.get(user=user)
    if request.method == 'POST':
        form = CurriculumForm(request.POST, request.FILES, instance=curriculum)
        if form.is_valid():
            user = form.save(commit=False)
            #Para cambiar los valores de ID por el texto
            user.sexo = request.POST.get('sexo_texto')
            user.genero = request.POST.get('genero_texto')
            user.paisResidencia = request.POST.get('pais_texto')
            user.carrera = request.POST.get('carrera_texto')
            if 'imagen_perfil' in request.FILES:  # borra si ya existe una foto de perfil
                if curriculum.imagen_perfil:
                    default_storage.delete(curriculum.imagen_perfil.path)
                    print('imagen de perfil borrada')
            if 'imagen_documento' in request.FILES:  # borra si ya existe una foto de perfil
                if curriculum.imagen_documento:
                    default_storage.delete(curriculum.imagen_documento.path)   
                    print('imagen de documento borrada')     

            # Verifica si ya existe una imagen o si el usuario proporcionó una nueva imagen
            if not curriculum.imagen_perfil and not 'imagen_perfil' in request.FILES:
                form.add_error('imagen_perfil', 'Debes subir una foto de perfil.')
            if not curriculum.imagen_documento and not 'imagen_documento' in request.FILES:
                form.add_error('imagen_documento', 'Debes subir una foto de documento.')

            # Solo guarda el formulario si no hay errores
            if not form.errors:
                curriculum = form.save()
                messages.success(request,'Curriculum actualizado correctamente')
            else:
                messages.error(request,'Error al actualizar el curriculum')
        else:
            messages.error(request,'Error al actualizar el curriculum')
    else:
        form = CurriculumForm(instance=curriculum)
    return render(request, 'estudiante/curriculum.html',{'formulario': form,'min_fecha':min_fecha})

#para la api
from rest_framework import viewsets
from .models import Curriculum
from .serializers import CurriculumSerializer

class CurriculumViewSet(viewsets.ModelViewSet):
    queryset = Curriculum.objects.all()
    serializer_class = CurriculumSerializer

from .models import Solicitud
from .serializers import SolicitudSerializer

class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer