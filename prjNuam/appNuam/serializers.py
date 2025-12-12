from django.utils import timezone
from rest_framework import serializers

from .models import CalificacionTributaria


class CalificacionTributariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalificacionTributaria
        fields = "__all__"

    def validate_anio(self, value):
        current_year = timezone.now().year
        if value < 2023:
            raise serializers.ValidationError("El año no puede ser menor a 2023.")
        if value > current_year:
            raise serializers.ValidationError("El año no puede ser mayor al año actual.")
        return value


class CreateUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["accionista", "inversionista"], write_only=True)
    emisores = serializers.PrimaryKeyRelatedField(
        queryset=CalificacionTributaria.objects.none(), # Placeholder, logic in view
        many=True, required=False, write_only=True
    ) 

    # Note: Complex logic usually goes to View or Service layer for this hybrid approach
    # Simplifying for strict requirement 
    class Meta:
        model = CalificacionTributaria # Hack strictly for serializer structure if not using Usuario model directly
        fields = "__all__"
    
    # Actually, let's use a proper Serializer
    
class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(min_length=4)
    tipo_cuenta = serializers.ChoiceField(choices=["accionista", "inversionista"])
    emisores_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
