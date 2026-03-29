from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_shareevent'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add followers M2M to Company
        migrations.AddField(
            model_name='company',
            name='followers',
            field=models.ManyToManyField(
                blank=True,
                related_name='followed_companies',
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        # Create CompanyMedia
        migrations.CreateModel(
            name='CompanyMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(
                    choices=[('image', 'Image'), ('video', 'Video'), ('document', 'Document')],
                    default='image',
                    max_length=20,
                )),
                ('file', models.FileField(upload_to='company_media/')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('caption', models.TextField(blank=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='media',
                    to='core.company',
                )),
                ('uploaded_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),

        # Create CompanyUpdate
        migrations.CreateModel(
            name='CompanyUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='company_update_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('company', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='updates',
                    to='core.company',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
