from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cupo, Ficho
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
import os
from django.conf import settings
from datetime import datetime
from django.db.models import Count
from django import template
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .serializers import FichoSerializer, CupoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

register = template.Library()

@register.filter
def get_fichos_adelante(ficho):
    return Ficho.objects.filter(cupo=ficho.cupo, fecha_creacion__lt=ficho.fecha_creacion).count()

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('validar_ficho_admin')
        else:
            return redirect('usuario')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('validar_ficho_admin')
            else:
                return redirect('usuario')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'core/login.html')
from .forms import EstudianteRegistroForm

def registro_estudiante(request):
    if request.method == 'POST':
        form = EstudianteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # No iniciar sesión automáticamente, solo redirigir a login
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = EstudianteRegistroForm()
    return render(request, 'core/registro_estudiante.html', {'form': form})

@login_required
def solicitar_ficho(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Verifica si ya tiene un ficho activo para el mismo día
    ficho_existente = Ficho.objects.filter(
        usuario=request.user,
        estado='activo',
        cupo__fecha=timezone.now().date()
    ).first()

    if ficho_existente:
        messages.warning(request, "Ya tienes un ficho activo. Cancela o espera a que expire antes de solicitar otro.")
        return redirect('home')

    servicios = Cupo.objects.filter(fecha=timezone.now().date(), cantidad_disponible__gt=0)
    # Recalcular cupos disponibles sumando los que se liberaron tras 10 minutos de validación
    servicios = list(servicios)
    for cupo in servicios:
        fichos_usados = Ficho.objects.filter(cupo=cupo, estado='usado', hora_validacion__isnull=False)
        liberados = 0
        for ficho in fichos_usados:
            if ficho.hora_validacion and (timezone.now() - ficho.hora_validacion).total_seconds() >= 600:
                liberados += 1
        cupo.cantidad_disponible += liberados
    usuario = request.user
    hoy = timezone.now().date()
    ficho_existente = Ficho.objects.filter(usuario=usuario, cupo__fecha=hoy, estado='activo').order_by('-fecha_creacion').first()
    puede_pedir = True
    mensaje_bloqueo = None
    fichos_adelante = None
    if ficho_existente:
        # Si la hora ya pasó y no fue validado, permitir nuevo ficho
        hora_ficho = ficho_existente.hora
        hora_actual = timezone.now().time()
        if ficho_existente.estado == 'activo':
            if hora_ficho < hora_actual:
                # Cambiar estado a 'expirado' (opcional)
                ficho_existente.estado = 'expirado'
                ficho_existente.save()
            else:
                puede_pedir = False
                mensaje_bloqueo = f"Ya tienes un ficho activo para hoy a las {hora_ficho}. Solo podrás pedir otro si pasa la hora o si tu ficho es validado."
                fichos_adelante = Ficho.objects.filter(cupo=ficho_existente.cupo, fecha_creacion__lt=ficho_existente.fecha_creacion).count()
        elif ficho_existente.estado == 'usado':
            puede_pedir = False
            mensaje_bloqueo = "Ya has validado tu ficho para hoy. Solo podrás pedir otro ficho mañana."
    if not puede_pedir:
        return render(request, 'core/solicitar_ficho.html', {'servicios': servicios, 'mensaje_bloqueo': mensaje_bloqueo, 'ficho_existente': ficho_existente, 'fichos_adelante': fichos_adelante})
    if request.method == 'POST':
        cupo_id = request.POST.get('cupo_id')
        hora = request.POST.get('hora')
        try:
            cupo = Cupo.objects.get(id=cupo_id, cantidad_disponible__gt=0)
        except Cupo.DoesNotExist:
            messages.error(request, 'No hay cupos disponibles para este servicio.')
            return redirect('solicitar_ficho')
        # Validar horario para comedores
        if cupo.nombre_servicio.lower() == 'comedores':
            if not (hora >= '11:30' and hora <= '13:30'):
                messages.error(request, 'El comedor solo está disponible de 11:30 a 13:30.')
                return redirect('solicitar_ficho')
        # Calcular posición en la fila
        fichos_anteriores = Ficho.objects.filter(cupo=cupo, fecha_creacion__lt=timezone.now()).count()
        # Crear el ficho
        ficho = Ficho.objects.create(usuario=request.user, cupo=cupo, hora=hora)
        # Generar QR con SOLO el ID del ficho
        qr_data = str(ficho.id)  # SOLO el ID
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_path = f"qr/ficho_{ficho.id}.png"
        ficho.codigo_qr.save(qr_path, ContentFile(buffer.getvalue()))
        ficho.save()
        # Actualizar cupo
        cupo.cantidad_disponible -= 1
        cupo.save()        # Calcular cuántos fichos hay por delante
        fichos_adelante = Ficho.objects.filter(cupo=cupo, fecha_creacion__lt=ficho.fecha_creacion).count()
        # Calcular el número de ficho
        numero_ficho = fichos_adelante + 1
        # Construir la URL absoluta para el QR
        qr_url = os.path.join(settings.MEDIA_URL, qr_path).replace('\\', '/')
        messages.success(request, 'Ficho generado exitosamente.')
        return redirect('usuario')
    return render(request, 'core/solicitar_ficho.html', {'servicios': servicios})

@login_required
def validar_ficho(request, ficho_id):
    ficho = Ficho.objects.get(id=ficho_id)
    # Calcular el número de ficho
    numero_ficho = Ficho.objects.filter(cupo=ficho.cupo, fecha_creacion__lt=ficho.fecha_creacion).count() + 1
    if request.method == 'POST':
        ficho.estado = 'usado'
        ficho.hora_validacion = timezone.now()
        ficho.save()
        messages.success(request, 'Ficho validado correctamente.')
        return redirect('usuario')
    return render(request, 'core/validar_ficho.html', {
        'ficho': ficho,
        'numero_ficho': numero_ficho
    })

@login_required
def cancelar_ficho(request, ficho_id):
    ficho = Ficho.objects.get(id=ficho_id, usuario=request.user)
    if ficho.estado == 'activo':
        if request.method == 'POST':
            ficho.estado = 'cancelado'
            ficho.save()
            # Devolver el cupo
            ficho.cupo.cantidad_disponible += 1
            ficho.cupo.save()
            messages.success(request, 'Ficho cancelado correctamente.')
            return redirect('usuario')
        return render(request, 'core/cancelar_ficho.html', {'ficho': ficho})
    else:
        messages.error(request, 'Este ficho no se puede cancelar.')
        return redirect('usuario')

@login_required
def ver_ficho(request):
    hoy = timezone.now().date()
    ficho = Ficho.objects.filter(usuario=request.user, cupo__fecha=hoy, estado='activo').order_by('-fecha_creacion').first()
    numero_ficho = None
    if ficho:
        numero_ficho = Ficho.objects.filter(cupo=ficho.cupo, fecha_creacion__lt=ficho.fecha_creacion).count() + 1
    return render(request, 'core/ver_ficho.html', {'ficho': ficho, 'numero_ficho': numero_ficho})

def usuario_view(request):
    from .models import Ficho
    if not request.user.is_authenticated:
        return redirect('login')
    hoy = timezone.now().date()
    ficho_existente = None
    if not request.user.is_staff:
        ficho_existente = Ficho.objects.filter(usuario=request.user, cupo__fecha=hoy, estado='activo').order_by('-fecha_creacion').first()
        historial_fichos = Ficho.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:20]
    else:
        ficho_existente = None
        historial_fichos = None
    ultimos_fichos = Ficho.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:3]
    return render(request, 'core/usuario.html', {
        'ficho_existente': ficho_existente,
        'es_admin': request.user.is_staff,
        'historial_fichos': historial_fichos,
        'ultimos_fichos': ultimos_fichos,
    })

def logout_view(request):
    logout(request)
    response = render(request, 'core/logout.html')
    # Invalida la caché para evitar volver atrás
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@staff_member_required
def panel_admin(request):
    from .models import Cupo  # Asegura que Cupo esté disponible siempre
    # Agregar cupo desde el formulario
    if request.method == 'POST':
        nombre_servicio = request.POST.get('nombre_servicio')
        fecha = request.POST.get('fecha')
        cantidad_total = request.POST.get('cantidad_total')
        if nombre_servicio and fecha and cantidad_total:
            Cupo.objects.create(
                nombre_servicio=nombre_servicio,
                fecha=fecha,
                cantidad_total=cantidad_total,
                cantidad_disponible=cantidad_total
            )
            messages.success(request, 'Cupo agregado correctamente.')
            return redirect('panel_admin')
    # Estadísticas
    total_fichos = Ficho.objects.count()
    fichos_hoy = Ficho.objects.filter(cupo__fecha=timezone.now().date()).count()
    fichos_usados = Ficho.objects.filter(estado__in=['usado', 'validado']).count()
    fichos_cancelados = Ficho.objects.filter(estado='cancelado').count()
    fichos_activos = Ficho.objects.filter(estado='activo').count()
    # Historial de validaciones
    historial = Ficho.objects.filter(estado__in=['usado', 'validado']).order_by('-fecha_creacion')[:50]
    # Cupos
    cupos = Cupo.objects.all().order_by('-fecha')
    return render(request, 'core/panel_admin.html', {
        'total_fichos': total_fichos,
        'fichos_hoy': fichos_hoy,
        'fichos_usados': fichos_usados,
        'fichos_cancelados': fichos_cancelados,
        'fichos_activos': fichos_activos,
        'historial': historial,
        'cupos': cupos
    })

@staff_member_required
def validar_ficho_admin(request):
    ficho_id = request.GET.get('codigo')
    ficho = None
    numero_ficho = None
    mensaje_error = None
    if ficho_id:
        try:
            ficho = Ficho.objects.get(id=ficho_id)
            numero_ficho = Ficho.objects.filter(cupo=ficho.cupo, fecha_creacion__lt=ficho.fecha_creacion).count() + 1
            if request.method == 'POST':
                ficho.estado = 'usado'
                ficho.hora_validacion = timezone.now()
                ficho.save()
                messages.success(request, 'Ficho validado correctamente.')
                return redirect('validar_ficho_admin')
        except Ficho.DoesNotExist:
            mensaje_error = 'Ficho no encontrado.'
    return render(request, 'core/validar_ficho_admin.html', {
        'ficho': ficho,
        'numero_ficho': numero_ficho,
        'mensaje_error': mensaje_error
    })

from django.shortcuts import render

def home(request):
    ficho_qr_url = None
    if request.user.is_authenticated:
        ficho = Ficho.objects.filter(usuario=request.user, estado='activo').first()
        if ficho and ficho.codigo_qr:
            # Siempre usa el atributo .url para obtener la URL de la imagen
            ficho_qr_url = ficho.codigo_qr.url
    return render(request, 'core/home.html', {'ficho_qr_url': ficho_qr_url})

class FichoListAPI(generics.ListCreateAPIView):
    serializer_class = FichoSerializer

    def get_queryset(self):
        hoy = timezone.now().date()
        return Ficho.objects.filter(usuario=self.request.user, estado='activo', cupo__fecha=hoy)

    def perform_create(self, serializer):
        user = self.request.user
        hoy = timezone.now().date()
        ficho_existente = Ficho.objects.filter(usuario=user, estado='activo', cupo__fecha=hoy).first()
        if ficho_existente:
            raise serializers.ValidationError("Ya tienes un ficho activo para hoy.")

        # Validación de hora para intervalos de 5 minutos entre 11:30 y 13:30
        hora_obj = serializer.validated_data.get('hora')
        if not hora_obj:
            raise serializers.ValidationError("Debes especificar la hora.")

        hora_inicio = datetime.strptime("11:30", "%H:%M").time()
        hora_fin = datetime.strptime("13:30", "%H:%M").time()

        if not (hora_inicio <= hora_obj <= hora_fin):
            raise serializers.ValidationError("Solo puedes solicitar fichos entre 11:30 y 13:30.")

        if hora_obj.minute % 5 != 0:
            raise serializers.ValidationError("Solo puedes solicitar fichos en intervalos de 5 minutos.")

        serializer.save(usuario=user)

from rest_framework.generics import ListAPIView
from .models import Cupo
from .serializers import CupoSerializer
from django.utils import timezone

class CupoDisponibleListAPI(ListAPIView):
    serializer_class = CupoSerializer

    def get_queryset(self):
        hoy = timezone.now().date()
        return Cupo.objects.filter(fecha=hoy, cantidad_disponible__gt=0)

class UsuarioAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            # agrega más campos si quieres
        })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_ficho(request, pk):
    from .models import Ficho
    try:
        ficho = Ficho.objects.get(pk=pk, usuario=request.user)
    except Ficho.DoesNotExist:
        return Response({'detail': 'Ficho no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    if ficho.estado != 'activo':
        return Response({'detail': 'Solo puedes cancelar fichos activos.'}, status=status.HTTP_400_BAD_REQUEST)
    ficho.estado = 'cancelado'
    ficho.save()
    return Response({'detail': 'Ficho cancelado.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validar_ficho_api(request):
    from .models import Ficho
    ficho_id = request.data.get('codigo')
    try:
        ficho = Ficho.objects.get(id=ficho_id)
    except Ficho.DoesNotExist:
        return Response({'valido': False, 'detail': 'Ficho no encontrado.'}, status=404)
    if ficho.estado == 'usado':
        return Response({'valido': True, 'usado': True, 'detail': 'Ficho ya fue usado.'})
    if ficho.estado != 'activo':
        return Response({'valido': False, 'detail': 'Ficho no está activo.'}, status=400)
    ficho.estado = 'usado'
    ficho.hora_validacion = timezone.now()
    ficho.save()
    return Response({'valido': True, 'usado': False, 'detail': 'Ficho validado y marcado como usado.'})

