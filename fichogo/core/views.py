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

register = template.Library()

@register.filter
def get_fichos_adelante(ficho):
    return Ficho.objects.filter(cupo=ficho.cupo, fecha_solicitud__lt=ficho.fecha_solicitud).count()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('usuario')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
            login(request, user)
            return redirect('usuario')
    else:
        form = EstudianteRegistroForm()
    return render(request, 'core/registro_estudiante.html', {'form': form})

@login_required
def solicitar_ficho(request):
    servicios = Cupo.objects.filter(fecha=timezone.now().date(), cantidad_disponible__gt=0)
    usuario = request.user
    hoy = timezone.now().date()
    ficho_existente = Ficho.objects.filter(usuario=usuario, cupo__fecha=hoy, estado='activo').order_by('-fecha_solicitud').first()
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
                fichos_adelante = Ficho.objects.filter(cupo=ficho_existente.cupo, fecha_solicitud__lt=ficho_existente.fecha_solicitud).count()
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
        fichos_anteriores = Ficho.objects.filter(cupo=cupo, fecha_solicitud__lt=timezone.now()).count()
        # Crear el ficho
        ficho = Ficho.objects.create(usuario=request.user, cupo=cupo, hora=hora)
        # Generar QR con la URL de validación
        qr_url_validacion = request.build_absolute_uri(f'/validar-ficho/{ficho.id}/')
        qr_img = qrcode.make(qr_url_validacion)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_path = f"qr/ficho_{ficho.id}.png"
        from django.core.files.storage import default_storage
        default_storage.save(qr_path, ContentFile(buffer.getvalue()))
        ficho.codigo_qr = qr_path
        ficho.save()
        # Actualizar cupo
        cupo.cantidad_disponible -= 1
        cupo.save()        # Calcular cuántos fichos hay por delante
        fichos_adelante = Ficho.objects.filter(cupo=cupo, fecha_solicitud__lt=ficho.fecha_solicitud).count()
        # Calcular el número de ficho
        numero_ficho = fichos_adelante + 1
        # Construir la URL absoluta para el QR
        qr_url = os.path.join(settings.MEDIA_URL, qr_path).replace('\\', '/')
        messages.success(request, 'Ficho generado exitosamente.')
        return render(request, 'core/ficho_confirmacion.html', {'ficho': ficho, 'qr_url': qr_url, 'fichos_adelante': fichos_adelante, 'numero_ficho': numero_ficho})
    return render(request, 'core/solicitar_ficho.html', {'servicios': servicios})

@login_required
def validar_ficho(request, ficho_id):
    ficho = Ficho.objects.get(id=ficho_id)
    # Calcular el número de ficho
    numero_ficho = Ficho.objects.filter(cupo=ficho.cupo, fecha_solicitud__lt=ficho.fecha_solicitud).count() + 1
    if request.method == 'POST':
        ficho.estado = 'usado'
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

def usuario_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # Mostrar el ficho activo de hoy si existe
    hoy = timezone.now().date()
    ficho_existente = Ficho.objects.filter(usuario=request.user, cupo__fecha=hoy, estado='activo').order_by('-fecha_solicitud').first()
    return render(request, 'core/usuario.html', {'ficho_existente': ficho_existente})

def logout_view(request):
    logout(request)
    return render(request, 'core/logout.html')

@staff_member_required
def panel_admin(request):
    # Estadísticas
    total_fichos = Ficho.objects.count()
    fichos_hoy = Ficho.objects.filter(cupo__fecha=timezone.now().date()).count()
    fichos_usados = Ficho.objects.filter(estado='usado').count()
    fichos_cancelados = Ficho.objects.filter(estado='cancelado').count()
    fichos_activos = Ficho.objects.filter(estado='activo').count()
    # Historial de validaciones
    historial = Ficho.objects.filter(estado='usado').order_by('-fecha_solicitud')[:50]
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
