from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_project_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Expand existing Page model
        migrations.AddField(
            model_name='page', name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page', name='industry',
            field=models.CharField(
                choices=[('tech','Technology'),('finance','Finance'),('health','Healthcare'),
                         ('edu','Education'),('energy','Energy'),('agriculture','Agriculture'),
                         ('manufacturing','Manufacturing'),('media','Media & Entertainment'),
                         ('retail','Retail & Commerce'),('other','Other')],
                default='other', max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='page', name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='page_covers/'),
        ),
        migrations.AddField(
            model_name='page', name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='page_logos/'),
        ),
        migrations.AddField(
            model_name='page', name='website',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page', name='followers',
            field=models.ManyToManyField(
                blank=True, related_name='followed_pages', to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='page', name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='page', name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owned_pages', to=settings.AUTH_USER_MODEL,
            ),
        ),
        # PagePost
        migrations.CreateModel(
            name='PagePost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='page_post_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='core.page')),
            ],
            options={'ordering': ['-created_at']},
        ),
        # PagePostReaction
        migrations.CreateModel(
            name='PagePostReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction', models.CharField(
                    choices=[('like','Like'),('love','Love'),('insightful','Insightful'),
                             ('celebrate','Celebrate'),('support','Support')],
                    default='like', max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='core.pagepost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_post_reactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('post', 'user')}},
        ),
        # PagePostShare
        migrations.CreateModel(
            name='PagePostShare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shares', to='core.pagepost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_post_shares', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('post', 'user')}},
        ),
    ]
