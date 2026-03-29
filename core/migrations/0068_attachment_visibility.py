from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_company_media_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='title',
            field=models.CharField(max_length=200, blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attachment',
            name='doc_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('general',      'General'),
                    ('financial',    'Financial Document'),
                    ('legal',        'Legal / Contract'),
                    ('technical',    'Technical Document'),
                    ('presentation', 'Presentation'),
                    ('proposal',     'Proposal'),
                    ('report',       'Report'),
                    ('other',        'Other'),
                ],
                default='general',
            ),
        ),
        migrations.AddField(
            model_name='attachment',
            name='visibility',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('public',      'Public — anyone can download'),
                    ('connections', 'Connections only'),
                    ('private',     'Private — only me'),
                ],
                default='connections',
            ),
        ),
        migrations.AddField(
            model_name='attachment',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
