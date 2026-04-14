from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for the CustomUser model."""

    model = User
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "is_email_verified",
        "created_at",
    ]
    list_filter = ["is_staff", "is_active", "is_email_verified", "country"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]

    # Fields shown when editing an existing user
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                    "profile_picture",
                    "date_of_birth",
                    "country",
                    "bio",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    # Fields shown when creating a new user via admin
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_email_verified",
                ),
            },
        ),
    )
