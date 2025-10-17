from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("-id")
    serializer_class = ProjectSerializer

    # Lectura pública; escritura autenticada (ajústalo si quieres solo admin)
    def get_permissions(self):
        if self.request.method in ("GET",):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
