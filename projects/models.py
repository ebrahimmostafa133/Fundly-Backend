from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, editable=False)

    class Meta:
        ordering = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.name)
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    tags = models.ManyToManyField(Tag, related_name='projects', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def avg_rating(self):
        average = self.ratings.aggregate(avg=Avg('score'))['avg']
        if average is None:
            return None
        return float(average)

    def __str__(self):
        return self.title


class Rating(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_ratings'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ## one user can only rate one project once
        unique_together = ('project', 'user') 
        ordering = ['-created_at']

    def __str__(self):
        return f'Rating {self.score} by {self.user_id} on project {self.project_id}'
