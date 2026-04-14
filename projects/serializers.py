from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Project, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class ProjectListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    owner = serializers.CharField(source='owner.username', read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'category',
            'tags',
            'status',
            'progress',
            'is_featured',
            'avg_rating',
            'owner',
        ]

    def get_avg_rating(self, project):
        # List and featured views add _avg on the query
        if hasattr(project, '_avg'):
            if project._avg is None:
                return None
            return float(project._avg)
        # Top-rated view adds avg on the query
        if hasattr(project, 'avg'):
            if project.avg is None:
                return None
            return float(project.avg)
        return project.avg_rating


class ProjectDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    owner = OwnerSerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'owner',
            'title',
            'description',
            'category',
            'tags',
            'status',
            'progress',
            'is_featured',
            'created_at',
            'updated_at',
            'avg_rating',
        ]

    def get_avg_rating(self, project):
        if hasattr(project, '_avg'):
            if project._avg is None:
                return None
            return float(project._avg)
        if hasattr(project, 'avg'):
            if project.avg is None:
                return None
            return float(project.avg)
        return project.avg_rating


class ProjectWriteSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'category',
            'tags',
            'status',
            'progress',
            'is_featured',
        ]

    def validate_progress(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError('Progress must be between 0 and 100.')
        return value

"""
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['score']

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value
"""