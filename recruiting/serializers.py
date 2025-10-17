from rest_framework import serializers
from .models import Application

class ApplicationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.ReadOnlyField(source="candidate.username")

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("candidate", "status", "match_score", "parsed_text", "created_at")
