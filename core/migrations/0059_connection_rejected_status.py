from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_profileview_viewer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
                default='pending',
                max_length=20,
            ),
        ),
    ]
