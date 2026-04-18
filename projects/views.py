from django.db.models import Avg, Count, F, Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Project, Tag
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CategorySerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectWriteSerializer,
    TagSerializer,
)


class ProjectListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request):
        projects = Project.objects.select_related('owner', 'category')
        projects = projects.prefetch_related('tags', 'images')
        projects = projects.annotate(_avg=Avg('ratings__value'))

        category_slug = request.query_params.get('category')
        tag_slug = request.query_params.get('tag')
        search_text = request.query_params.get('search')
        owner_id = request.query_params.get('owner')

        if category_slug:
            projects = projects.filter(category__slug__iexact=category_slug)
        if tag_slug:
            projects = projects.filter(tags__slug__iexact=tag_slug).distinct()
        if owner_id:
            projects = projects.filter(owner_id=owner_id)
        if search_text:
            projects = projects.filter(
                Q(title__icontains=search_text)
                | Q(description__icontains=search_text)
                | Q(tags__name__icontains=search_text)
                | Q(tags__slug__icontains=search_text)
            ).distinct()

        serializer = ProjectListSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectWriteSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(owner=request.user)
            project_qs = Project.objects.select_related('owner', 'category')
            project = project_qs.prefetch_related('tags', 'images').get(id=project.id)
            data = ProjectDetailSerializer(project)
            return Response(data.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_object(self, project_id):
        project = Project.objects.select_related('owner', 'category')
        project = project.prefetch_related('tags', 'images')
        return get_object_or_404(project, id=project_id)

    def get(self, request, project_id):
        project = self.get_object(project_id)
        data = ProjectDetailSerializer(project)
        return Response(data.data)

    def put(self, request, project_id):
        project = self.get_object(project_id)
        self.check_object_permissions(request, project)
        serializer = ProjectWriteSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = ProjectDetailSerializer(project)
            return Response(data.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, project_id):
        project = self.get_object(project_id)
        self.check_object_permissions(request, project)
        serializer = ProjectWriteSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = ProjectDetailSerializer(project)
            return Response(data.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        self.check_object_permissions(request, project)
        if project.progress >= 25:
            message = 'Cannot cancel a project with progress 25% or higher.'
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        project.status = 'cancelled'
        project.save(update_fields=['status', 'updated_at'])
        data = ProjectDetailSerializer(project)
        return Response(data.data)


class ProjectSimilarView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        tag_ids = list(project.tags.values_list('pk', flat=True))
        if len(tag_ids) == 0:
            return Response([])

        others = Project.objects.exclude(pk=project.pk)
        others = others.select_related('owner', 'category')
        others = others.prefetch_related('tags', 'images')
        others = others.filter(tags__id__in=tag_ids)
        tag_filter = Q(tags__id__in=tag_ids)
        others = others.annotate(shared=Count('tags', filter=tag_filter, distinct=True))
        others = others.annotate(_avg=Avg('ratings__value'))
        others = others.order_by('-shared', '-created_at')

        already_added = set()
        similar_projects = []
        for row in others:
            if row.pk in already_added:
                continue
            already_added.add(row.pk)
            similar_projects.append(row)
            if len(similar_projects) == 4:
                break

        data = ProjectListSerializer(similar_projects, many=True)
        return Response(data.data)


class FeaturedProjectsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        featured_projects = Project.objects.filter(is_featured=True)
        featured_projects = featured_projects.select_related('owner', 'category')
        featured_projects = featured_projects.prefetch_related('tags', 'images')
        featured_projects = featured_projects.annotate(_avg=Avg('ratings__value'))
        featured_projects = featured_projects.order_by('-created_at')[:5]
        data = ProjectListSerializer(featured_projects, many=True)
        return Response(data.data)


class TopRatedProjectsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        projects = Project.objects.all()
        projects = projects.select_related('owner', 'category')
        projects = projects.prefetch_related('tags', 'images')
        projects = projects.annotate(avg=Avg('ratings__value'))
        projects = projects.filter(status='active')
        # Put projects with no rating at the end
        projects = projects.order_by(F('avg').desc(nulls_last=True), '-created_at')
        projects = projects[:5]
        data = ProjectListSerializer(projects, many=True)
        return Response(data.data)
