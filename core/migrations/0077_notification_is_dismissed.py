from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0076_notification_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='is_dismissed',
            field=models.BooleanField(default=False),
        ),
    ]
