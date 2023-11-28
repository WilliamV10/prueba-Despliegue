from django.urls import path, include

from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from .views import *  # Importo todas las vistas de la app porque si no zzz, una por una XD

router =DefaultRouter()
router.register(r'curriculum', CurriculumViewSet)
router.register(r'solicitud', SolicitudViewSet)
urlpatterns = [
    #falta la url de la pagina principal
    path('registrarse/', registrar, name='registrarse'),  #Vista para registrarse como estudiante
    path('', login_view, name='login'),#vista de inicio de sesion
    path('index/', index, name='index'),  #Vista de prueba de iniciar Sesion
    path('logout/', logout_view, name='logout'), #para cerrar sesion
    path('index-admin/',indexAdmin, name='index-admin'),#vista de prueba de admin
    path('index-estudiante/',indexUser, name='index-estudiante'),#vista de prueba de estudiante
    path('seguimiento/',seguimiento, name='seguimiento'),#vista de prueba de estudiante
    path('crearEstudiante/',crearEstudiante, name='crearEstudiante'),#vista para crear estudiante
    path('editarEstudiante/<int:id>',editarEstudiante, name='editarEstudiante'),#vista para editar estudiante
    path('eliminarEstudiante/<int:id>',eliminarEstudiante, name='eliminarEstudiante'),#vista para eliminar estudiante
    path('crearCurriculum/<int:id>/', crearCurriculum, name='crearCurriculum'),#vista para ver el curriculum del estudiante
    path('api', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)