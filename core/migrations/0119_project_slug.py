from django.db import migrations, models
from django.utils.text import slugify

RESERVED = {'create', 'generate-description'}


def fill_slugs(apps, schema_editor):
    Project = apps.get_model('core', 'Project')
    used = set(Project.objects.exclude(slug__isnull=True).values_list('slug', flat=True))
    for p in Project.objects.filter(slug__isnull=True).order_by('pk'):
        base = slugify(p.title or '')[:100].strip('-') or 'project'
        if base in RESERVED or base.isdigit():
            base = f'{base}-project'
        slug, n = base, 2
        while slug in used:
            slug = f'{base}-{n}'
            n += 1
        used.add(slug)
        Project.objects.filter(pk=p.pk).update(slug=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0118_pricing_enabled'),
    ]

    operations = [
        # No index yet: on Postgres a SlugField index brings a second "_like" index, and the
        # unique step below creates that same index again (DuplicateTable). Adding the column
        # unindexed means the indexes are created exactly once, by the AlterField.
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, null=True, db_index=False),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, null=True, unique=True),
        ),
    ]
