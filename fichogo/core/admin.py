from django.contrib import admin
from .models import Cupo, Ficho

@admin.register(Cupo)
class CupoAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'fecha', 'cantidad_total', 'cantidad_disponible')
    search_fields = ('nombre_servicio',)
    list_filter = ('fecha',)

@admin.register(Ficho)
class FichoAdmin(admin.ModelAdmin):
    def nombre_estudiante(self, obj):
        return obj.usuario.first_name
    nombre_estudiante.short_description = 'Nombre'

    def numero_ficho(self, obj):
        return Ficho.objects.filter(cupo=obj.cupo, fecha_creacion__lt=obj.fecha_creacion).count() + 1
    numero_ficho.short_description = 'N° Ficho'

    list_display = ('usuario', 'cupo', 'hora', 'fecha_creacion', 'estado', 'numero_ficho')
    search_fields = ('usuario__username', 'usuario__first_name', 'cupo__nombre_servicio')
    list_filter = ('estado', 'fecha_creacion')
    actions = ["marcar_como_usado"]

    @admin.action(description="Marcar como usado")
    def marcar_como_usado(self, request, queryset):
        updated = queryset.update(estado='usado')
        self.message_user(request, f"{updated} ficho(s) marcados como usado.")
# Registra tus modelos aquí
