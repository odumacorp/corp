from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_connection_rejected_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add action fields to Notification
        migrations.AddField(
            model_name='notification',
            name='action_type',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='notification',
            name='action_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='project_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        # Update notification_type choices
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=[
                    ('connected', 'Connected'),
                    ('message_sent', 'Message Sent'),
                    ('collaboration', 'Collaboration'),
                    ('project_proposal', 'Project Proposal'),
                    ('other', 'Other'),
                ],
                default='other',
                max_length=20,
            ),
        ),
        # Create ProjectProposal model
        migrations.CreateModel(
            name='ProjectProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True)),
                ('amount', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')],
                    default='pending', max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='proposals',
                    to='core.project',
                )),
                ('from_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_proposals_sent',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]
