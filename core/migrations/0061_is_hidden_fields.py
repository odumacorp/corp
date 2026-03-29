from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0060_notification_action_fields_projectproposal'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='group',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='projectcomment',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
    ]
