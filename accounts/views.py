from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from decouple import config

from .permissions import is_admin_user
from .serializers import (
    AdminUserSerializer,
    ChangePasswordSerializer,
    DeleteAccountSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    RegisterSerializer,
)
from .utils import send_activation_email, send_password_reset_email

User = get_user_model()


# ─── Registration ────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    POST /api/auth/register/
    Create a new user account and send an activation email.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Send activation email
    try:
        send_activation_email(user, request)
    except Exception:
        # Log the error in production; don't block registration
        pass

    return Response(
        {
            "message": "Registration successful. Please check your email to activate your account.",
            "user": ProfileSerializer(user).data,
        },
        status=status.HTTP_201_CREATED,
    )


# ─── Email Activation ───────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([AllowAny])
def activate_account(request, uidb64, token):
    """
    GET /api/auth/activate/<uidb64>/<token>/
    Verify user email with the activation token.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"error": "Invalid activation link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.is_email_verified:
        return Response(
            {"message": "Account is already verified."},
            status=status.HTTP_200_OK,
        )

    if default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        return Response(
            {"message": "Email verified successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "Invalid or expired activation link."},
        status=status.HTTP_400_BAD_REQUEST,
    )


# ─── Login ───────────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    POST /api/auth/login/
    Authenticate user and return JWT tokens.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_email_verified:
        return Response(
            {"error": "Please verify your email address before logging in."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if not user.is_active:
        return Response(
            {"error": "This account has been deactivated."},
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "message": "Login successful.",
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            "user": ProfileSerializer(user).data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    """
    POST /api/auth/google-login/
    Verify Google OAuth2 token and return JWT tokens.
    """
    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), config("GOOGLE_CLIENT_ID")
        )

        email = idinfo["email"]
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "is_email_verified": True,
            },
        )

        if not user.is_active:
            return Response(
                {"error": "This account has been deactivated."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Ensure email is verified if user already existed
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": ProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    except ValueError:
        return Response(
            {"error": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST
        )


# ─── Logout ──────────────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    POST /api/auth/logout/
    Blacklist the refresh token to log the user out.
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response(
            {"error": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response(
            {"error": "Invalid or already blacklisted token."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "Logged out successfully."},
        status=status.HTTP_200_OK,
    )


# ─── Profile ────────────────────────────────────────────────────────────────


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile(request):
    """
    GET   /api/auth/profile/  — get own profile
    PATCH /api/auth/profile/  — update own profile
    """
    user = request.user

    if request.method == "GET":
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH
    serializer = ProfileSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


# ─── Delete Account ─────────────────────────────────────────────────────────


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    DELETE /api/auth/profile/delete/
    Deactivate user account (soft delete). Requires password confirmation.
    """
    serializer = DeleteAccountSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)

    user = request.user
    user.is_active = False
    user.save(update_fields=["is_active"])

    return Response(
        {"message": "Account deactivated successfully."},
        status=status.HTTP_200_OK,
    )


# ─── Change Password ────────────────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    POST /api/auth/password/change/
    Change password for authenticated users.
    """
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)

    user = request.user
    user.set_password(serializer.validated_data["new_password"])
    user.save()

    return Response(
        {"message": "Password changed successfully."},
        status=status.HTTP_200_OK,
    )


# ─── Password Reset (request) ───────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    POST /api/auth/password/reset/
    Send a password reset email.
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    user = User.objects.get(email=email)

    try:
        send_password_reset_email(user)
    except Exception:
        return Response(
            {"error": "Failed to send reset email. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {"message": "Password reset email sent. Check your inbox."},
        status=status.HTTP_200_OK,
    )


# ─── Password Reset (confirm) ───────────────────────────────────────────────


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    """
    POST /api/auth/password/reset/confirm/<uidb64>/<token>/
    Set a new password using the reset token.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"error": "Invalid reset link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(user, token):
        return Response(
            {"error": "Invalid or expired reset link."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user.set_password(serializer.validated_data["new_password"])
    user.save()

    return Response(
        {"message": "Password reset successfully. You can now log in."},
        status=status.HTTP_200_OK,
    )


# ─── Admin: User List ────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_user_list(request):
    """
    GET /api/auth/users/
    Admin-only endpoint to list all users.
    """
    if not is_admin_user(request.user):
        return Response(
            {"error": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    users = User.objects.all()
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
