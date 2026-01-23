from django.contrib import admin
from .models import PasswordResetToken, PasswordResetAttempt


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used', 'ip_address')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__username', 'token', 'uid')
    readonly_fields = ('token', 'uid', 'created_at', 'expires_at')
    ordering = ('-created_at',)


@admin.register(PasswordResetAttempt)
class PasswordResetAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email', 'ip_address')
    readonly_fields = ('email', 'ip_address', 'created_at')
    ordering = ('-created_at',)
