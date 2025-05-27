# Serializadores para Django REST Framework
from rest_framework import serializers
from .models import Ficho, Cupo

class FichoSerializer(serializers.ModelSerializer):
    fecha_solicitud = serializers.DateTimeField(source='fecha_creacion', format='%Y-%m-%d %H:%M', read_only=True)
    cupo_nombre_servicio = serializers.CharField(source='cupo.nombre_servicio', read_only=True)
    codigo_qr = serializers.SerializerMethodField()

    class Meta:
        model = Ficho
        fields = [
            'id',
            'estado',
            'hora',
            'cupo',  # <-- AGREGA ESTA LÍNEA
            'fecha_solicitud',
            'cupo_nombre_servicio',
            'codigo_qr',
        ]

    def get_codigo_qr(self, obj):
        request = self.context.get('request')
        if obj.codigo_qr and hasattr(obj.codigo_qr, 'url'):
            if request:
                return request.build_absolute_uri(obj.codigo_qr.url)
            else:
                return obj.codigo_qr.url
        return None

class CupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupo
        fields = '__all__'
