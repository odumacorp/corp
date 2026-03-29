from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0078_meeting'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='duration',
            field=models.PositiveIntegerField(default=60, help_text='Duration in minutes'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='zoom_meeting_id',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='meeting',
            name='zoom_join_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='meeting',
            name='zoom_start_url',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='meeting',
            name='zoom_password',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='meeting',
            name='recording_status',
            field=models.CharField(
                blank=True, default='', max_length=20,
                choices=[('', 'None'), ('processing', 'Processing'), ('completed', 'Available')],
            ),
        ),
        migrations.AddField(
            model_name='meeting',
            name='recording_url',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
    ]
