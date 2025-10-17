from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Application
from .serializers import ApplicationSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related("candidate", "project").all().order_by("-created_at")
    serializer_class = ApplicationSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    # Si no eres admin (is_staff), solo ves tus propias aplicaciones
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(candidate=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)
