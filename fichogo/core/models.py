from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File

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
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=[('activo', 'Activo'), ('cancelado', 'Cancelado')], default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    codigo_qr = models.ImageField(upload_to='qr/', blank=True, null=True)
    hora_validacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ficho de {self.usuario.username} para {self.cupo.nombre_servicio} ({self.hora})"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)  # Guarda primero para tener el ID
        if creating:
            qr_data = str(self.id)  # Solo el ID
            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            self.codigo_qr.save(f'ficho_{self.usuario.username}_{self.id}.png', File(buffer), save=False)
            super().save(update_fields=['codigo_qr'])  # Guarda el QR

