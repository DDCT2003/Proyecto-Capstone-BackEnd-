from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
from datetime import timedelta


class PasswordResetToken(models.Model):
    """
    Modelo para almacenar tokens de recuperación de contraseña
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    uid = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token', 'uid']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self):
        return f"Reset token for {self.user.email} - {'Used' if self.is_used else 'Active'}"
    
    def is_valid(self):
        """Verifica si el token es válido y no ha expirado"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.is_used = True
        self.save()
    
    @staticmethod
    def generate_token():
        """Genera un token seguro único"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_uid(user):
        """Genera un UID basado en el ID del usuario"""
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        return urlsafe_base64_encode(force_bytes(user.pk))
    
    @classmethod
    def create_for_user(cls, user, ip_address=None):
        """Crea un nuevo token de reseteo para un usuario"""
        # Invalidar tokens anteriores no usados
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Crear nuevo token
        token = cls.generate_token()
        uid = cls.generate_uid(user)
        expires_at = timezone.now() + timedelta(hours=1)
        
        return cls.objects.create(
            user=user,
            token=token,
            uid=uid,
            expires_at=expires_at,
            ip_address=ip_address
        )


class PasswordResetAttempt(models.Model):
    """
    Modelo para rastrear intentos de reseteo de contraseña (rate limiting)
    """
    ip_address = models.GenericIPAddressField()
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    @classmethod
    def can_request_reset(cls, ip_address, max_attempts=3, time_window_hours=1):
        """
        Verifica si una IP puede solicitar un reseteo
        Máximo 3 intentos por hora
        """
        time_threshold = timezone.now() - timedelta(hours=time_window_hours)
        recent_attempts = cls.objects.filter(
            ip_address=ip_address,
            created_at__gte=time_threshold
        ).count()
        
        return recent_attempts < max_attempts
    
    @classmethod
    def record_attempt(cls, ip_address, email):
        """Registra un intento de reseteo"""
        return cls.objects.create(ip_address=ip_address, email=email)
