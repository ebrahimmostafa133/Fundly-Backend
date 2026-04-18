from django.urls import path
from .views import ProjectCommentsView, ReplyView, CommentDetailView

urlpatterns = [
    path('project/<int:project_id>/',   ProjectCommentsView.as_view(), name='project-comments'),
    path('<int:comment_id>/reply/',     ReplyView.as_view(),           name='comment-reply'),
    path('<int:comment_id>/',           CommentDetailView.as_view(),   name='comment-detail'),
]
