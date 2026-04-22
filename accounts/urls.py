from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    # Registration & Activation
    path("register/", views.register, name="register"),
    path(
        "activate/<uidb64>/<token>/",
        views.activate_account,
        name="activate",
    ),
    # Login / Logout / Token Refresh
    path("login/", views.login, name="login"),
    path("google-login/", views.google_login, name="google-login"),
    path("logout/", views.logout, name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # Profile
    path("profile/", views.profile, name="profile"),
    path(
        "profile/delete/",
        views.delete_account,
        name="delete-account",
    ),
    # Password Management
    path(
        "password/change/",
        views.change_password,
        name="change-password",
    ),
    path(
        "password/reset/",
        views.password_reset_request,
        name="password-reset",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password-reset-confirm",
    ),
    # Admin
    path("users/", views.admin_user_list, name="admin-user-list"),
]
