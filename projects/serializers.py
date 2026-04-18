from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Project, ProjectImage, Tag


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
        fields = ['id', 'email', 'first_name', 'last_name']


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    owner = serializers.CharField(source='owner.email', read_only=True)
    progress = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'category',
            'tags',
            'images',
            'target',
            'start_time',
            'end_time',
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

    def get_progress(self, project):
        return project.progress


class ProjectDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    owner = OwnerSerializer(read_only=True)
    progress = serializers.SerializerMethodField()
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
            'images',
            'target',
            'start_time',
            'end_time',
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

    def get_progress(self, project):
        return project.progress


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
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'category',
            'tags',
            'images',
            'target',
            'start_time',
            'end_time',
            'status',
            'is_featured',
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if self.instance is not None:
            if start_time is None:
                start_time = self.instance.start_time
            if end_time is None:
                end_time = self.instance.end_time

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {'end_time': 'End time must be after start time.'}
            )
        return attrs

    def create(self, validated_data):
        ## removes the 'images' key from the validated_data dictionary and assigns the array of files to the images variable
        images = validated_data.pop('images', [])
        ## creates the project and returns it
        project = super().create(validated_data)
        ## creates the project images and returns them
        for image in images:
            ProjectImage.objects.create(project=project, image=image)
        return project

    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        project = super().update(instance, validated_data)
        if images is not None:
            project.images.all().delete()
            for image in images:
                ProjectImage.objects.create(project=project, image=image)
        return project