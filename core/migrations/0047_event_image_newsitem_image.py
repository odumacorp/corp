from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_newsitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='event_images/'),
        ),
        migrations.AddField(
            model_name='newsitem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='news_images/'),
        ),
    ]
