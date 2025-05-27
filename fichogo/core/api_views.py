# filepath: fichogo/core/api_views.py
from rest_framework import generics
from .models import Ficho, Cupo
from .serializers import FichoSerializer, CupoSerializer
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from datetime import time, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import qrcode
from io import BytesIO
from django.core.files import File


class FichoListAPI(generics.ListCreateAPIView):
    serializer_class = FichoSerializer

    def get_queryset(self):
        hoy = timezone.now().date()
        return Ficho.objects.filter(usuario=self.request.user, estado='activo', cupo__fecha=hoy)

    def perform_create(self, serializer):
        user = self.request.user
        hora_ficho = serializer.validated_data.get('hora')
        hora_inicio = time(11, 30)
        hora_fin = time(13, 30)
        print("DEBUG - Hora del ficho:", hora_ficho)
        if not (hora_inicio <= hora_ficho <= hora_fin):
            raise ValidationError(f"Solo puedes pedir fichos entre 11:30 y 13:30. Hora seleccionada: {hora_ficho}")
        serializer.save(usuario=user)

class CupoDisponibleListAPI(generics.ListAPIView):
    serializer_class = CupoSerializer

    def get_queryset(self):
        hoy = timezone.now().date()
        return Cupo.objects.filter(fecha=hoy, cantidad_disponible__gt=0)

class RegistroAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Usuario y contraseña requeridos'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'El usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username})

class Command(BaseCommand):
    help = 'Cancela fichos que han pasado 5 minutos de la hora estipulada'

    def handle(self, *args, **kwargs):
        ahora = timezone.now()
        fichos = Ficho.objects.filter(estado='activo')
        for ficho in fichos:
            if ficho.cupo and ficho.cupo.hora:  # Asumiendo que Cupo tiene un campo 'hora'
                hora_ficho = timezone.make_aware(
                    datetime.combine(ficho.cupo.fecha, ficho.cupo.hora)
                )
                if ahora > hora_ficho + timedelta(minutes=5):
                    ficho.estado = 'cancelado'
                    ficho.save()
                    self.stdout.write(f'Ficho {ficho.id} cancelado por expiración')

class HistorialFichosHoyAPI(generics.ListAPIView):
    serializer_class = FichoSerializer

    def get_queryset(self):
        return Ficho.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_creacion')[:5]

class UsuarioAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_staff or user.is_superuser,  # <-- agrega esto
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_ficho_admin(request):
    ficho_id = request.GET.get('codigo')
    try:
        ficho = Ficho.objects.get(id=ficho_id)
        if ficho.estado != 'activo':
            return Response({'valido': True, 'usado': True})
        ficho.estado = 'cancelado'  # O 'usado' si tienes ese estado
        ficho.save()
        return Response({'valido': True, 'usado': False})
    except Ficho.DoesNotExist:
        return Response({'valido': False})

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