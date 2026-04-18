from django.urls import path
from .views import ReportCreateView

urlpatterns = [
    path('create/', ReportCreateView.as_view(), name='create-report'),
]
