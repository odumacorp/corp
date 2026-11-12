import re

from django.db import migrations, models
from django.utils.text import slugify

RESERVED = {'share', 'share-to-feed'}


def _context_part(conv, Project):
    if conv.context_type == 'project' and conv.project_id:
        title = Project.objects.filter(pk=conv.project_id).values_list('title', flat=True).first()
        return slugify(title or '')[:25].strip('-') or 'project'
    if conv.context_type in ('post', 'proposal', 'collab'):
        return conv.context_type
    return ''


def _base(context, usernames):
    parts = [context] + [slugify(u.replace('.', '-')) for u in usernames[:2]]
    base = '-'.join(p for p in parts if p)[:70]
    if base in RESERVED or base.isdigit():
        base = f'{base}-chat'
    return base


def rename_one_member_chats(apps, schema_editor):
    """Chats whose members were added one at a time got named after the first member only
    ('admin', 'admin-2', ...). Rename them after all members and keep the old address."""
    Conversation = apps.get_model('core', 'Conversation')
    Project = apps.get_model('core', 'Project')
    taken = set(Conversation.objects.values_list('slug', flat=True))
    for conv in Conversation.objects.order_by('pk'):
        usernames = sorted(conv.participants.values_list('username', flat=True))
        if len(usernames) < 2 or not conv.slug:
            continue
        context = _context_part(conv, Project)
        current_base = re.sub(r'-\d+$', '', conv.slug)
        one_member = {_base(context, [u]) for u in usernames}
        if current_base not in one_member and conv.slug not in one_member:
            continue                      # named correctly (or by hand): leave it alone
        base = _base(context, usernames)
        slug, n = base, 2
        while slug in taken and slug != conv.slug:
            slug = f'{base}-{n}'
            n += 1
        if slug == conv.slug:
            continue
        taken.discard(conv.slug)
        taken.add(slug)
        Conversation.objects.filter(pk=conv.pk).update(legacy_slug=conv.slug, slug=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0121_group_page_job_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='legacy_slug',
            field=models.CharField(blank=True, db_index=True, max_length=80, null=True),
        ),
        migrations.RunPython(rename_one_member_chats, migrations.RunPython.noop),
    ]
