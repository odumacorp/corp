from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0055_groupdiscussioncomment_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='category',
            field=models.CharField(
                choices=[('innovation', 'Innovation'), ('invention', 'Invention')],
                default='innovation',
                max_length=20,
            ),
        ),
    ]
