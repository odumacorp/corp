from django.db import migrations, models


def migrate_old_statuses(apps, schema_editor):
    Project = apps.get_model('core', 'Project')
    Project.objects.filter(status='in_progress').update(status='development')
    Project.objects.filter(status='completed').update(status='maintenance')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0064_projectcollaboration_extend'),
    ]

    operations = [
        migrations.RunPython(migrate_old_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('draft',       'Planning'),
                    ('design',      'Design'),
                    ('development', 'Development'),
                    ('testing',     'Testing & QA'),
                    ('deployment',  'Deployment'),
                    ('maintenance', 'Maintenance'),
                ],
                default='draft',
            ),
        ),
    ]
