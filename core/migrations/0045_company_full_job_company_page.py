from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_pageview_browser_pageview_city_pageview_country_and_more'),
    ]

    operations = [
        # Add new fields to Company
        migrations.AddField(
            model_name='company',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='companies',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='tagline',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
        migrations.AlterField(
            model_name='company',
            name='industry',
            field=models.CharField(
                choices=[
                    ('technology', 'Technology'),
                    ('finance', 'Finance & Banking'),
                    ('health', 'Health & Medicine'),
                    ('agriculture', 'Agriculture'),
                    ('education', 'Education'),
                    ('energy', 'Energy'),
                    ('manufacturing', 'Manufacturing'),
                    ('retail', 'Retail & E-commerce'),
                    ('media', 'Media & Entertainment'),
                    ('real_estate', 'Real Estate'),
                    ('logistics', 'Logistics & Transport'),
                    ('consulting', 'Consulting'),
                    ('other', 'Other'),
                ],
                default='other', max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='company_type',
            field=models.CharField(
                choices=[
                    ('startup', 'Startup'),
                    ('sme', 'SME'),
                    ('enterprise', 'Enterprise'),
                    ('ngo', 'NGO / Non-Profit'),
                    ('government', 'Government'),
                    ('other', 'Other'),
                ],
                default='other', max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='size',
            field=models.CharField(
                blank=True, default='',
                choices=[
                    ('1-10', '1–10 employees'),
                    ('11-50', '11–50 employees'),
                    ('51-200', '51–200 employees'),
                    ('201-500', '201–500 employees'),
                    ('500+', '500+ employees'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='location',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='website',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='company',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='company',
            name='founded_year',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='company_logos/'),
        ),
        migrations.AddField(
            model_name='company',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='company_covers/'),
        ),
        migrations.AddField(
            model_name='company',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='company',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Add company_page FK to Job
        migrations.AddField(
            model_name='job',
            name='company_page',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='jobs',
                to='core.company',
            ),
        ),
    ]
