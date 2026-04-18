import django_filters

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    tag = django_filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    class Meta:
        model = Project
        fields = ['category', 'tag']
