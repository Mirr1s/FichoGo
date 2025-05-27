from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from .api_views import FichoListAPI, CupoDisponibleListAPI, RegistroAPI, HistorialFichosHoyAPI, UsuarioAPI

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('solicitar-ficho/', views.solicitar_ficho, name='solicitar_ficho'),
    path('registro/', views.registro_estudiante, name='registro_estudiante'),
    path('usuario/', views.usuario_view, name='usuario'),
    path('validar-ficho/<int:ficho_id>/', views.validar_ficho, name='validar_ficho'),
    path('cancelar-ficho/<int:ficho_id>/', views.cancelar_ficho, name='cancelar_ficho'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('validar-ficho-admin/', views.validar_ficho_admin, name='validar_ficho_admin'),
    path('ver-ficho/', views.ver_ficho, name='ver_ficho'),
    path('api/fichos/', FichoListAPI.as_view(), name='api_fichos'),
    path('api/cupos/', CupoDisponibleListAPI.as_view(), name='api_cupos'),
    path('api/login/', obtain_auth_token, name='api_login'),
    path('api/registro/', RegistroAPI.as_view(), name='api_registro'),
    path('api/fichos/<int:pk>/cancelar/', views.cancelar_ficho, name='api_cancelar_ficho'),
    path('api/historial-hoy/', HistorialFichosHoyAPI.as_view(), name='historial-hoy'),
    path('api/usuario/', UsuarioAPI.as_view(), name='api_usuario'),
    path('api/validar-ficho-admin/', views.validar_ficho_admin, name='validar_ficho_admin'),
    path('api/validar-ficho/', views.validar_ficho_api, name='validar_ficho_api'),
]