from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0003_delete_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='end_time',
            field=models.DateTimeField(default='2026-01-01T00:00:00Z'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='start_time',
            field=models.DateTimeField(default='2026-01-01T00:00:00Z'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='target',
            field=models.DecimalField(
                decimal_places=2,
                default=1,
                max_digits=12,
                validators=[MinValueValidator(1)],
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ProjectImage',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('image', models.ImageField(upload_to='project_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='images',
                        to='projects.project',
                    ),
                ),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
