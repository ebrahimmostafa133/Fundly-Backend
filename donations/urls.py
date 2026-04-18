from django.urls import path
from . import views
app_name = "donations"
urlpatterns = [
    path("donate/<int:project_id>/", views.donate, name="donate"),
    path("project/<int:project_id>/", views.project_details, name="project-details"),
    path("my-donations/", views.user_donations, name="user-donations"),
]