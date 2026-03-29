from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_is_hidden_content'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SurveyResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('ui_design', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('ui_consistency', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('ux_navigation', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('ux_findability', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('usability_tasks', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('usability_controls', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('exp_satisfaction', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('exp_recommend', models.CharField(blank=True, choices=[('yes', 'Yes'), ('maybe', 'Maybe'), ('no', 'No')], max_length=5)),
                ('func_reliability', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('func_missing', models.TextField(blank=True)),
                ('comments', models.TextField(blank=True)),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='survey_responses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
    ]
