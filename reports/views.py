from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import Report
from .serializers import ReportSerializer

class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')
        comment = serializer.validated_data.get('comment')

        already_reported = Report.objects.filter(
            user=user,
            project=project,
            comment=comment
        ).exists()

        if already_reported:
            raise ValidationError("You have already reported this")

        serializer.save(user=user)