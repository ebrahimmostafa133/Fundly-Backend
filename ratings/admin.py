from django.contrib import admin
from .models import Rating

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'value', 'created_at']
    list_filter = ['value']