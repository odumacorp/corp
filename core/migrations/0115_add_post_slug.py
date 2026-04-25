from django.db import migrations, models
from django.utils.text import slugify


def backfill_post_slugs(apps, schema_editor):
    Post = apps.get_model('core', 'Post')
    for post in Post.objects.all():
        base = slugify(post.title)[:80] or 'post'
        post.slug = f"{base}-{post.pk}"
        post.save(update_fields=['slug'])


class Migration(migrations.Migration):
    # Must be non-atomic: AddField creates a deferred LIKE index that conflicts
    # with the AlterField's deferred LIKE index inside a single transaction.
    atomic = False

    dependencies = [
        ('core', '0114_conversation_readable_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, default=''),
        ),
        migrations.RunPython(backfill_post_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
    ]
