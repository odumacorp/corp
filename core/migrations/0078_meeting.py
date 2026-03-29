import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_notification_is_dismissed'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=200)),
                ('room_id', models.CharField(blank=True, max_length=32, unique=True)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('active', 'Active'), ('ended', 'Ended')], default='scheduled', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_meetings', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(blank=True, related_name='meetings', to=settings.AUTH_USER_MODEL)),
                ('conversation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meetings', to='core.conversation')),
            ],
        ),
    ]
