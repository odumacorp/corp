from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0063_surveyresponse'),
    ]
    operations = [
        migrations.AddField(
            model_name='projectcollaboration',
            name='counter_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='projectcollaboration',
            name='conversation',
            field=models.OneToOneField(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='project_collab',
                to='core.conversation',
            ),
        ),
        migrations.AlterField(
            model_name='projectcollaboration',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[('pending','Pending'),('accepted','Accepted'),('declined','Declined'),
                         ('countered','Countered'),('on_hold','On Hold'),('reviewing','Reviewing')],
                default='pending',
            ),
        ),
    ]
