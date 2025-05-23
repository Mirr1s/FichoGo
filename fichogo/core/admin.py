from django.contrib import admin
from .models import Cupo, Ficho

@admin.register(Cupo)
class CupoAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'fecha', 'cantidad_total', 'cantidad_disponible')
    search_fields = ('nombre_servicio',)
    list_filter = ('fecha',)

@admin.register(Ficho)
class FichoAdmin(admin.ModelAdmin):
    def numero_ficho(self, obj):
        return Ficho.objects.filter(cupo=obj.cupo, fecha_solicitud__lt=obj.fecha_solicitud).count() + 1
    numero_ficho.short_description = 'N° Ficho'

    list_display = ('usuario', 'cupo', 'fecha_solicitud', 'estado', 'numero_ficho')
    search_fields = ('usuario__username', 'cupo__nombre_servicio')
    list_filter = ('estado', 'fecha_solicitud')
# Registra tus modelos aquí
