from django.urls import path
from .views import RatingCreateView, RatingListView, RatingStatsView, UserRatingView

urlpatterns = [
    path('project/<int:project_id>/', RatingStatsView.as_view(), name='project-rating-stats'),
    path('user/<int:project_id>/', UserRatingView.as_view(), name='user-rating'),
    path('create/', RatingCreateView.as_view(), name='create-rating'),
]
