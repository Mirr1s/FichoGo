from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

# Define aquí las rutas específicas de la app core
urlpatterns = [
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
]
