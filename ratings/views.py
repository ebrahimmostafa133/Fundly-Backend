from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Avg, Count
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


class RatingStatsView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        stats = Rating.objects.filter(project_id=project_id).aggregate(
            avg_rating=Avg('value'),
            count=Count('id')
        )
        return Response({
            'avg_rating': stats['avg_rating'] or 0,
            'count': stats['count'] or 0
        })


class UserRatingView(generics.GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id, *args, **kwargs):
        """Get the current user's rating for a project"""
        try:
            rating = Rating.objects.get(user=request.user, project_id=project_id)
            serializer = self.get_serializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response({'value': None}, status=status.HTTP_200_OK)

    def put(self, request, project_id, *args, **kwargs):
        """Update the current user's rating for a project"""
        try:
            rating = Rating.objects.get(user=request.user, project_id=project_id)
            serializer = self.get_serializer(rating, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Rating.DoesNotExist:
            raise NotFound("You haven't rated this project yet")