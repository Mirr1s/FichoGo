from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Ficho
from datetime import datetime

class Command(BaseCommand):
    help = 'Cancela automáticamente los fichos que han pasado su hora de asistencia y siguen activos.'

    def handle(self, *args, **options):
        ahora = timezone.localtime()
        fichos = Ficho.objects.filter(estado='activo')
        total_cancelados = 0
        for ficho in fichos:
            fecha = ficho.cupo.fecha
            hora = ficho.hora
            if fecha and hora:
                dt_ficho = datetime.combine(fecha, hora)
                dt_ficho = timezone.make_aware(dt_ficho)
                if ahora > dt_ficho:
                    ficho.estado = 'cancelado'
                    ficho.save()
                    total_cancelados += 1
        self.stdout.write(self.style.SUCCESS(f'Se cancelaron {total_cancelados} fichos vencidos.'))
