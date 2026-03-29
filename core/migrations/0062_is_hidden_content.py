from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_is_hidden_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='newsitem',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='job',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
