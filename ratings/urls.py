from django.urls import path
from .views import RatingCreateView, RatingListView

urlpatterns = [
    path('project/<int:project_id>/', RatingListView.as_view(), name='project-ratings'),
    path('create/', RatingCreateView.as_view(), name='create-rating'),
]
