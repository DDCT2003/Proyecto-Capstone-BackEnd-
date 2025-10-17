from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "candidate", "project", "status", "created_at")
    list_filter = ("status", "project")
    search_fields = ("candidate__username",)




