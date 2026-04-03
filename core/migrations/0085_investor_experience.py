from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0084_pitch_deck_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Investor profile fields on UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='ticket_size_min',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Minimum cheque size in USD', max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='ticket_size_max',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Maximum cheque size in USD', max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='preferred_sectors',
            field=models.CharField(blank=True, default='', help_text='Comma-separated sectors of interest', max_length=500),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='geography_focus',
            field=models.CharField(blank=True, default='', help_text='Geographic markets of interest', max_length=255),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='investment_thesis',
            field=models.TextField(blank=True, default='', help_text='Brief investment thesis or mandate'),
        ),
        # funding_stage on Project
        migrations.AddField(
            model_name='project',
            name='funding_stage',
            field=models.CharField(
                blank=True, default='',
                choices=[
                    ('', 'Not specified'), ('pre_seed', 'Pre-Seed'), ('seed', 'Seed'),
                    ('pre_series_a', 'Pre-Series A'), ('series_a', 'Series A'),
                    ('series_b', 'Series B+'), ('grant', 'Grant / Non-dilutive'),
                ],
                max_length=20,
            ),
        ),
        # PitchRequest model
        migrations.CreateModel(
            name='PitchRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, default='')),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('scheduled', 'Scheduled')],
                    default='pending', max_length=20,
                )),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('responded_at', models.DateTimeField(blank=True, null=True)),
                ('response_note', models.TextField(blank=True, default='')),
                ('investor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pitch_requests_sent',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pitch_requests',
                    to='core.project',
                )),
            ],
            options={'ordering': ['-requested_at']},
        ),
        migrations.AddConstraint(
            model_name='pitchrequest',
            constraint=models.UniqueConstraint(fields=['project', 'investor'], name='unique_pitch_request'),
        ),
    ]
