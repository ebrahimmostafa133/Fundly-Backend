from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'comment', 'reason', 'created_at']
    list_filter = ['reason']
    search_fields = ['user__email', 'project__title']
    readonly_fields = ['created_at']