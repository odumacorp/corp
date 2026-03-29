from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_project_sdlc_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(
                    max_length=20,
                    choices=[
                        ('whatsapp',  'WhatsApp'),
                        ('telegram',  'Telegram'),
                        ('twitter',   'Twitter / X'),
                        ('facebook',  'Facebook'),
                        ('linkedin',  'LinkedIn'),
                        ('instagram', 'Instagram'),
                        ('copy_link', 'Copy Link'),
                        ('other',     'Other'),
                    ],
                    default='other',
                )),
                ('share_type', models.CharField(
                    max_length=20,
                    choices=[
                        ('individual', 'Individual / DM'),
                        ('group',      'Group / Channel'),
                        ('general',    'General'),
                    ],
                    default='general',
                )),
                ('content_type', models.CharField(
                    max_length=20,
                    choices=[
                        ('project', 'Project'),
                        ('post',    'Post'),
                        ('profile', 'Profile'),
                        ('page',    'Page'),
                        ('other',   'Other'),
                    ],
                    blank=True,
                )),
                ('object_id',   models.PositiveIntegerField(null=True, blank=True)),
                ('shared_url',  models.URLField(max_length=600, blank=True)),
                ('shared_at',   models.DateTimeField(auto_now_add=True)),
                ('ip_address',  models.GenericIPAddressField(null=True, blank=True)),
                ('shared_by', models.ForeignKey(
                    null=True, blank=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='share_events',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-shared_at'],
            },
        ),
    ]
