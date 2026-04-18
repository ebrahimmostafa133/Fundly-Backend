from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.conf import settings


class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_ratings'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user} rated {self.project} → {self.value}/5"

    @staticmethod
    def get_average_rating(project_id):
        project_ratings = Rating.objects.filter(project_id=project_id)
        result = project_ratings.aggregate(Avg('value'))
        avg = result['value__avg']
    
        if avg == None:
            return 0
        else:
            return round(avg, 1)