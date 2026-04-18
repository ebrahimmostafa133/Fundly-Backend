from django.urls import path

from .views import (
    CategoryListCreateView,
    FeaturedProjectsView,
    ProjectCancelView,
    ProjectDetailView,
    ProjectListCreateView,
    ProjectSimilarView,
    TagListCreateView,
    TopRatedProjectsView,
)

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('featured/', FeaturedProjectsView.as_view(), name='project-featured'),
    path('top-rated/', TopRatedProjectsView.as_view(), name='project-top-rated'),
    path('<int:project_id>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/cancel/', ProjectCancelView.as_view(), name='project-cancel'),
    path('<int:project_id>/similar/', ProjectSimilarView.as_view(), name='project-similar'),
]
