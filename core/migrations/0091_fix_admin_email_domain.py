from django.db import migrations


def fix_odumaconnect_emails(apps, schema_editor):
    """Replace @odumaconnect.com with @odumacorp.com for any stored user emails."""
    User = apps.get_model('core', 'CustomUser')
    for user in User.objects.filter(email__icontains='@odumaconnect.com'):
        user.email = user.email.replace('@odumaconnect.com', '@odumacorp.com')
        user.save(update_fields=['email'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0090_alter_connection_status'),
    ]

    operations = [
        migrations.RunPython(fix_odumaconnect_emails, migrations.RunPython.noop),
    ]
