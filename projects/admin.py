from django.contrib import admin

from .models import Category, Project, Rating, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    readonly_fields = ['slug', 'created_at']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    readonly_fields = ['slug']
    search_fields = ['name']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['project__title', 'user__username']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'owner',
        'category',
        'status',
        'progress',
        'is_featured',
        'avg_rating_display',
    ]
    list_filter = ['status', 'is_featured', 'category']
    search_fields = ['title', 'description']
    filter_horizontal = ['tags']
    actions = ['make_featured', 'make_not_featured']

    @admin.display(description='Avg rating')
    def avg_rating_display(self, obj):
        return obj.avg_rating

    @admin.action(description='Mark selected projects as featured')
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'Marked {count} project(s) as featured.')

    @admin.action(description='Mark selected projects as not featured')
    def make_not_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'Removed featured flag from {count} project(s).')
