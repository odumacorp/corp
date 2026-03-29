from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_attachmentdownload'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Rebuild Group with new fields
        migrations.AddField(
            model_name='group',
            name='creator',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_groups',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='industry',
            field=models.CharField(
                choices=[('tech','Technology'),('finance','Finance'),('health','Healthcare'),
                         ('edu','Education'),('energy','Energy'),('agriculture','Agriculture'),
                         ('manufacturing','Manufacturing'),('other','Other')],
                default='other', max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='group',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='group_covers/'),
        ),
        migrations.AddField(
            model_name='group',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        # GroupMembership
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[('invited','Invited'),('pending','Pending'),
                             ('accepted','Accepted'),('declined','Declined')],
                    default='pending', max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='memberships', to='core.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='group_memberships', to=settings.AUTH_USER_MODEL)),
                ('invited_by', models.ForeignKey(blank=True, null=True,
                                                  on_delete=django.db.models.deletion.SET_NULL,
                                                  related_name='sent_group_invites', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('group', 'user')}},
        ),
        # GroupDiscussion
        migrations.CreateModel(
            name='GroupDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='discussions', to='core.group')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='group_discussions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        # GroupDiscussionComment
        migrations.CreateModel(
            name='GroupDiscussionComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='comments', to='core.groupdiscussion')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='group_discussion_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['created_at']},
        ),
    ]
