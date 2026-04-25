from django.db import migrations, models


def backfill_readable_slugs(apps, schema_editor):
    from django.utils.text import slugify
    Conversation = apps.get_model('core', 'Conversation')
    used = set()

    for conv in Conversation.objects.prefetch_related('participants').select_related('project'):
        usernames = list(
            conv.participants.values_list('username', flat=True).order_by('username')
        )
        parts = []
        if conv.context_type == 'project' and conv.project_id:
            try:
                title = conv.project.title
                parts.append(slugify(title)[:25].strip('-'))
            except Exception:
                parts.append('project')
        elif conv.context_type == 'post':
            parts.append('post')
        elif conv.context_type == 'proposal':
            parts.append('proposal')
        elif conv.context_type == 'collab':
            parts.append('collab')

        for u in usernames[:2]:
            parts.append(slugify(u.replace('.', '-')))

        if not parts:
            import uuid
            h = uuid.uuid4().hex
            slug = f"{h[:8]}-{h[8:12]}-{h[12:16]}"
        else:
            base = '-'.join(p for p in parts if p)[:70]
            slug = base
            n = 2
            while slug in used:
                slug = f'{base}-{n}'
                n += 1

        used.add(slug)
        conv.slug = slug
        conv.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0113_add_conversation_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='slug',
            field=models.CharField(blank=True, max_length=80, unique=True),
        ),
        migrations.RunPython(backfill_readable_slugs, migrations.RunPython.noop),
    ]
