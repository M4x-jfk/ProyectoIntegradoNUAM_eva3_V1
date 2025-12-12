from rest_framework import viewsets

from .models import CalificacionTributaria
from .serializers import CalificacionTributariaSerializer


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = CalificacionTributaria.objects.all()
    serializer_class = CalificacionTributariaSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import hashlib
from .models import Usuario, Rol, UsuarioRol, Accionista, Inversionista, Emisor, EmisorUsuario
from .serializers import RegistroSerializer

class RegisterInvestorView(APIView):
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if data['tipo_cuenta'] != 'inversionista':
                 return Response({"error": "Wrong endpoint type"}, status=400)
            
            with transaction.atomic():
                 user = Usuario.objects.create(
                     username=data['username'],
                     email=data['email'],
                     nombre=data['nombre'],
                     apellido=data['apellido'],
                     password_hash=hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
                 )
                 rol, _ = Rol.objects.get_or_create(nombre="INVERSIONISTA")
                 UsuarioRol.objects.create(usuario=user, rol=rol)
                 Inversionista.objects.create(usuario=user, tipo_inversionista="Retail")
            
            return Response({"message": "Inversionista creado"}, status=201)
        return Response(serializer.errors, status=400)

class RegisterShareholderView(APIView):
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            if data['tipo_cuenta'] != 'accionista':
                 return Response({"error": "Wrong endpoint type"}, status=400)
            
            with transaction.atomic():
                 user = Usuario.objects.create(
                     username=data['username'],
                     email=data['email'],
                     nombre=data['nombre'],
                     apellido=data['apellido'],
                     password_hash=hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
                 )
                 rol, _ = Rol.objects.get_or_create(nombre="ACCIONISTA")
                 UsuarioRol.objects.create(usuario=user, rol=rol)
                 Accionista.objects.create(usuario=user)
                 
                 if 'emisores_ids' in data:
                     for eid in data['emisores_ids']:
                         em = Emisor.objects.filter(pk=eid).first()
                         if em:
                             EmisorUsuario.objects.create(usuario=user, emisor=em, rol_emisor="ACCIONISTA")
            
            return Response({"message": "Accionista creado"}, status=201)
        return Response(serializer.errors, status=400)
