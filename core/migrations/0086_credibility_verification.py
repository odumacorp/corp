from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_investor_experience'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # UserProfile: verification fields
        migrations.AddField(
            model_name='userprofile',
            name='verification_status',
            field=models.CharField(
                choices=[('unverified','Unverified'),('pending','Pending Review'),('verified','Verified'),('rejected','Rejected')],
                default='unverified', max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='verified_by',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='verifications_granted', to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Project: review fields
        migrations.AddField(
            model_name='project',
            name='review_status',
            field=models.CharField(
                choices=[('draft','Draft'),('under_review','Under Review'),('approved','Approved'),('featured','Featured'),('rejected','Rejected')],
                default='draft', max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='reviewed_by',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='projects_reviewed', to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='review_note',
            field=models.TextField(blank=True, default=''),
        ),
        # VerificationRequest model
        migrations.CreateModel(
            name='VerificationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio_statement', models.TextField(blank=True, default='', help_text='Why should you be verified?')),
                ('linkedin_url', models.URLField(blank=True, default='')),
                ('website_url', models.URLField(blank=True, default='')),
                ('notes', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default='pending', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_note', models.TextField(blank=True, default='')),
                ('id_document', models.FileField(blank=True, null=True, upload_to='verification_docs/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_requests', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verification_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-submitted_at']},
        ),
    ]
