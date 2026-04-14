from django.urls import path

from .views import (
    FeaturedProjectsView,
    ProjectCancelView,
    ProjectDetailView,
    ProjectListCreateView,
    ProjectSimilarView,
    TopRatedProjectsView,
)

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('featured/', FeaturedProjectsView.as_view(), name='project-featured'),
    path('top-rated/', TopRatedProjectsView.as_view(), name='project-top-rated'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/cancel/', ProjectCancelView.as_view(), name='project-cancel'),
    path('<int:project_id>/similar/', ProjectSimilarView.as_view(), name='project-similar'),
]
