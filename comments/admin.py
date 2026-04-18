from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'is_reply', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__email']
    raw_id_fields = ['user', 'project', 'parent']
