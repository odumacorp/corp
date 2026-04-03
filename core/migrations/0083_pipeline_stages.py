from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0082_project_proposal_status_and_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='pipeline_stage',
            field=models.CharField(
                choices=[
                    ('idea', 'Idea Stage'),
                    ('validation', 'Validation Stage'),
                    ('investment', 'Investment Stage'),
                    ('growth', 'Growth Stage'),
                ],
                default='idea',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='stage_status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('pending_approval', 'Pending Approval'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='active',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='StageProgressionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_stage', models.CharField(max_length=20)),
                ('to_stage', models.CharField(max_length=20)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                    default='pending',
                    max_length=20,
                )),
                ('admin_note', models.TextField(blank=True, default='')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stage_requests', to='core.project')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stage_requests_made', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stage_requests_reviewed', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-requested_at'],
            },
        ),
    ]
