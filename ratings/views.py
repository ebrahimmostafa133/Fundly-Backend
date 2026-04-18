from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Rating
from .serializers import RatingSerializer

class RatingCreateView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        if project.owner == self.request.user:
            raise PermissionDenied("You can't rate your own project")
        serializer.save(user=self.request.user)


class RatingListView(generics.ListAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Rating.objects.filter(project_id=project_id)