from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_group_discussion_likes_comment_replies'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='groupdiscussioncomment',
            name='likes',
            field=models.ManyToManyField(
                blank=True,
                related_name='liked_group_comments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
