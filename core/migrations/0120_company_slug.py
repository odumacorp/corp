from django.db import migrations, models
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    Company = apps.get_model('core', 'Company')
    used = set(Company.objects.exclude(slug__isnull=True).values_list('slug', flat=True))
    for c in Company.objects.filter(slug__isnull=True).order_by('pk'):
        base = slugify(c.name or '')[:100].strip('-') or 'company'
        if base.isdigit():
            base = f'{base}-company'
        slug, n = base, 2
        while slug in used:
            slug = f'{base}-{n}'
            n += 1
        used.add(slug)
        Company.objects.filter(pk=c.pk).update(slug=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0119_project_slug'),
    ]

    operations = [
        # Added without an index first: on Postgres the unique step below creates the
        # SlugField's "_like" index, and creating it twice fails (see 0119).
        migrations.AddField(
            model_name='company',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, null=True, db_index=False),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='company',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, null=True, unique=True),
        ),
    ]
