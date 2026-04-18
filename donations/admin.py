from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ["user", "project", "amount", "created_at"]
    search_fields = ["user__email", "project__title"]