from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ProjectCommentsView(APIView):
    """
    GET  /api/comments/project/<project_id>/   — list all top-level comments + their replies
    POST /api/comments/project/<project_id>/   — add a comment to a project
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request, project_id):
        comments = Comment.objects.filter(
            project_id=project_id,
            parent=None          # top-level only — replies are nested inside
        ).select_related('user').prefetch_related('replies__user')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(
                user=request.user,
                project_id=project_id,
                parent=None
            )
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReplyView(APIView):
    """
    POST /api/comments/<comment_id>/reply/  — reply to a comment
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        parent_comment = get_object_or_404(Comment, id=comment_id, parent=None)
        # prevent replying to a reply (keep nesting to 1 level)
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(
                user=request.user,
                project=parent_comment.project,
                parent=parent_comment
            )
            return Response(
                CommentSerializer(reply).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    """
    PATCH  /api/comments/<id>/  — edit your own comment
    DELETE /api/comments/<id>/  — delete your own comment
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self, comment_id, user):
        return get_object_or_404(Comment, id=comment_id)

    def patch(self, request, comment_id):
        comment = self.get_object(comment_id, request.user)
        self.check_object_permissions(request, comment)
        serializer = CommentCreateSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CommentSerializer(comment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = self.get_object(comment_id, request.user)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
