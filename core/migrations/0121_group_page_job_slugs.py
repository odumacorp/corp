from django.db import migrations, models
from django.utils.text import slugify

# (model, source field, words taken by other routes under the same prefix, fallback)
TARGETS = [
    ('Group', 'name', {'create'}, 'group'),
    ('Page', 'title', {'create'}, 'page'),
    ('Job', 'title', {'post', 'create'}, 'job'),
]


def fill_slugs(apps, schema_editor):
    for model_name, field, reserved, fallback in TARGETS:
        Model = apps.get_model('core', model_name)
        used = set(Model.objects.exclude(slug__isnull=True).values_list('slug', flat=True))
        for obj in Model.objects.filter(slug__isnull=True).order_by('pk'):
            base = slugify(getattr(obj, field) or '')[:100].strip('-') or fallback
            if base in reserved or base.isdigit():
                base = f'{base}-{fallback}'
            slug, n = base, 2
            while slug in used:
                slug = f'{base}-{n}'
                n += 1
            used.add(slug)
            Model.objects.filter(pk=obj.pk).update(slug=slug)


def add(name):
    # Unindexed first: on Postgres the unique step creates the SlugField "_like" index,
    # and creating it twice fails (see 0119).
    return migrations.AddField(model_name=name, name='slug',
                               field=models.SlugField(blank=True, max_length=120, null=True, db_index=False))


def make_unique(name):
    return migrations.AlterField(model_name=name, name='slug',
                                 field=models.SlugField(blank=True, max_length=120, null=True, unique=True))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0120_company_slug'),
    ]

    operations = [
        add('group'), add('page'), add('job'),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        make_unique('group'), make_unique('page'), make_unique('job'),
    ]
