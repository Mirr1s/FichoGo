from django.db import models
# NOTA: Si ves errores de importación en el editor, ignóralos si estás en un entorno fuera de Django. Estas importaciones funcionan correctamente en un entorno Django real.
from django.conf import settings

class Cupo(models.Model):
    nombre_servicio = models.CharField(max_length=100)
    cantidad_total = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    fecha = models.DateField()

    def __str__(self):
        return f"{self.nombre_servicio} ({self.fecha})"

class Ficho(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cupo = models.ForeignKey(Cupo, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    hora = models.TimeField()
    codigo_qr = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=[('activo', 'Activo'), ('usado', 'Usado'), ('cancelado', 'Cancelado')], default='activo')
    hora_validacion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Ficho de {self.usuario.username} para {self.cupo.nombre_servicio} ({self.fecha_solicitud.date()})"
