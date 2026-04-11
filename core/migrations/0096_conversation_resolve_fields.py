from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0095_custom_industry'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='is_resolved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conversation',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='auto_replied',
            field=models.BooleanField(default=False),
        ),
    ]
