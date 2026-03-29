from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_add_project_video2'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='link',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
