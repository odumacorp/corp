from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0083_pipeline_stages'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='problem_statement',
            field=models.TextField(blank=True, default='', verbose_name='Problem Statement'),
        ),
        migrations.AddField(
            model_name='project',
            name='solution_overview',
            field=models.TextField(blank=True, default='', verbose_name='Solution Overview'),
        ),
        migrations.AddField(
            model_name='project',
            name='market_opportunity',
            field=models.TextField(blank=True, default='', verbose_name='Market Opportunity'),
        ),
        migrations.AddField(
            model_name='project',
            name='business_model',
            field=models.TextField(blank=True, default='', verbose_name='Business Model'),
        ),
        migrations.AddField(
            model_name='project',
            name='traction',
            field=models.TextField(blank=True, default='', verbose_name='Traction / Validation'),
        ),
        migrations.AddField(
            model_name='project',
            name='funding_requirement',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Funding Requirement'),
        ),
        migrations.AddField(
            model_name='project',
            name='use_of_funds',
            field=models.TextField(blank=True, default='', verbose_name='Use of Funds'),
        ),
        migrations.AddField(
            model_name='project',
            name='team_overview',
            field=models.TextField(blank=True, default='', verbose_name='Team'),
        ),
    ]
