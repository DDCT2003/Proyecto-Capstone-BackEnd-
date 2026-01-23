from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import logging
from .serializers import (
    RegisterSerializer, MeSerializer, UserUpdateSerializer, 
    ChangePasswordSerializer, AdminUserSerializer, EmailTokenObtainPairSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .models import PasswordResetToken, PasswordResetAttempt
from .email_service import send_password_reset_email, send_password_reset_confirmation

logger = logging.getLogger(__name__)


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener tokens JWT usando email en lugar de username.
    El frontend envía: { "email": "correo@ejemplo.com", "password": "..." }
    """
    serializer_class = EmailTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que los administradores gestionen usuarios.
    - GET /api/accounts/users/ - Listar todos los usuarios
    - POST /api/accounts/users/ - Crear nuevo usuario
    - GET /api/accounts/users/{id}/ - Ver detalle de un usuario
    - PUT/PATCH /api/accounts/users/{id}/ - Actualizar usuario
    - DELETE /api/accounts/users/{id}/ - Eliminar usuario
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserSerializer
        return MeSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



class UpdateMeView(generics.UpdateAPIView):
    """
    Actualiza el perfil del usuario autenticado.
    URL: /accounts/me/update/  (ya definida en urls.py)
    Método: PUT o PATCH
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # siempre operar sobre el usuario autenticado
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "La contraseña actual no es correcta."}, status=status.HTTP_400_BAD_REQUEST)
        user.setPassword(serializer.validated_data["new_password"]) if hasattr(user, "setPassword") else user.set_password(serializer.validated_data["new_password"])
        user.save()
        # Mantener la sesión activa tras el cambio
        try:
            update_session_auth_hash(request, user)
        except Exception:
            pass
        return Response({"ok": True})


class PasswordResetRequestView(APIView):
    """
    Endpoint para solicitar reseteo de contraseña
    POST /api/accounts/password-reset/request/
    Body: { "email": "usuario@email.com" }
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def get_client_ip(self, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            # Por seguridad, siempre retorna 200 incluso con errores de validación
            return Response(
                {"detail": "Si el correo existe, recibirás instrucciones para restablecer tu contraseña."},
                status=status.HTTP_200_OK
            )
        
        email = serializer.validated_data['email']
        ip_address = self.get_client_ip(request)
        
        # Rate limiting: máximo 3 intentos por hora
        if not PasswordResetAttempt.can_request_reset(ip_address):
            logger.warning(f"Rate limit exceeded para IP {ip_address}")
            return Response(
                {"detail": "Demasiados intentos. Por favor, intenta más tarde."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Registrar intento
        PasswordResetAttempt.record_attempt(ip_address, email)
        
        # Buscar usuario (pero no revelar si existe o no)
        try:
            user = User.objects.get(email=email)
            
            # Crear token de reseteo
            reset_token = PasswordResetToken.create_for_user(user, ip_address)
            
            # Enviar email
            user_name = user.first_name or user.username
            send_password_reset_email(
                user_email=user.email,
                user_name=user_name,
                uid=reset_token.uid,
                token=reset_token.token
            )
            
            logger.info(f"✅ Token de reseteo creado para {email}")
            
        except User.DoesNotExist:
            # No hacer nada, pero registrar el intento
            logger.info(f"⚠️ Intento de reseteo para email no existente: {email}")
        
        # Siempre retornar 200 por seguridad (no revelar si el email existe)
        return Response(
            {"detail": "Si el correo existe, recibirás instrucciones para restablecer tu contraseña."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """
    Endpoint para confirmar reseteo de contraseña
    POST /api/accounts/password-reset/confirm/
    Body: { "uid": "...", "token": "...", "new_password": "..." }
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"detail": "Datos inválidos", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Decodificar UID para obtener el ID del usuario
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Buscar token válido
            reset_token = PasswordResetToken.objects.filter(
                user=user,
                uid=uid,
                token=token,
                is_used=False
            ).first()
            
            if not reset_token:
                logger.warning(f"Token no encontrado para user {user_id}")
                return Response(
                    {"detail": "El enlace de recuperación es inválido o ya fue utilizado."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar si el token expiró
            if not reset_token.is_valid():
                logger.warning(f"Token expirado para user {user_id}")
                return Response(
                    {"detail": "El enlace de recuperación ha expirado. Solicita uno nuevo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizar contraseña
            user.set_password(new_password)
            user.save()
            
            # Marcar token como usado
            reset_token.mark_as_used()
            
            # Enviar email de confirmación
            user_name = user.first_name or user.username
            send_password_reset_confirmation(
                user_email=user.email,
                user_name=user_name
            )
            
            logger.info(f"✅ Contraseña actualizada exitosamente para {user.email}")
            
            return Response(
                {"detail": "Contraseña actualizada exitosamente"},
                status=status.HTTP_200_OK
            )
            
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Error en reseteo de contraseña: {str(e)}")
            return Response(
                {"detail": "El enlace de recuperación es inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )
