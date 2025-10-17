from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "priority", "start_date", "end_date")
    search_fields = ("title",)
    list_filter = ("priority",)
