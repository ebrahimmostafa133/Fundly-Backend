from rest_framework import serializers
from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ["id", "project", "amount", "created_at"]
        read_only_fields = ["id", "project", "created_at"]


# ─── user history ─────────────────────────────────────────────────────────
class UserDonationSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title")

    class Meta:
        model = Donation
        fields = ["id", "project_title", "amount", "created_at"]