from django.db import migrations, models
import uuid


def populate_slugs(apps, schema_editor):
    Conversation = apps.get_model('core', 'Conversation')
    used = set()
    for conv in Conversation.objects.all():
        h = uuid.uuid4().hex
        slug = f"{h[:8]}-{h[8:12]}-{h[12:16]}"
        while slug in used:
            h = uuid.uuid4().hex
            slug = f"{h[:8]}-{h[8:12]}-{h[12:16]}"
        used.add(slug)
        conv.slug = slug
        conv.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0112_clear_website_link_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='slug',
            field=models.CharField(blank=True, max_length=32, default=''),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='conversation',
            name='slug',
            field=models.CharField(blank=True, max_length=32, unique=True),
        ),
    ]
