from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, request=None):
    """
    Send an account activation email with a verification link.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # Build activation URL — in production, point to your frontend
    frontend_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    activation_link = f"{frontend_base}/activate/{uid}/{token}"

    subject = "Fundly — Activate Your Account"
    message = (
        f"Hi {user.first_name},\n\n"
        f"Thanks for signing up for Fundly! Please click the link below "
        f"to verify your email address:\n\n"
        f"{activation_link}\n\n"
        f"If you didn't create this account, you can safely ignore this email.\n\n"
        f"— The Fundly Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user):
    """
    Send a password-reset email with a reset link.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    frontend_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_base}/reset-password/{uid}/{token}"

    subject = "Fundly — Reset Your Password"
    message = (
        f"Hi {user.first_name},\n\n"
        f"We received a request to reset your password. "
        f"Click the link below to set a new password:\n\n"
        f"{reset_link}\n\n"
        f"If you didn't request this, you can safely ignore this email.\n\n"
        f"— The Fundly Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
