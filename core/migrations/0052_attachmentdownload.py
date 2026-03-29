from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_comment_likes_replies'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('attachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='core.attachment')),
                ('downloaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attachment_downloads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-downloaded_at'],
            },
        ),
    ]
