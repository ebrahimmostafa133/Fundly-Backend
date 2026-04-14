
from django.db import models
from django.conf import settings
 

class Report(models.Model):
    
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('offensive', 'Offensive'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    comment = models.ForeignKey(
        
        'comments.Comment',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} reported {self.project or self.comment}"