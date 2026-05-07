from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _sync_social_apps(sender, **kwargs):
    """Keep the Google SocialApp DB record in sync with env-var credentials.

    allauth 65.x merges both DB records AND settings APP configs into one list,
    so we must NOT put credentials in SOCIALACCOUNT_PROVIDERS['APP'] — only the
    DB record should exist. This handler runs after every migrate so the record
    always reflects the current GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET env vars.
    """
    from django.conf import settings
    try:
        from allauth.socialaccount.models import SocialApp
    except Exception:
        return

    client_id = getattr(settings, '_GOOGLE_CLIENT_ID', '')
    secret = getattr(settings, '_GOOGLE_CLIENT_SECRET', '')
    if not client_id:
        return

    # Remove duplicates if any exist, then upsert a single clean record.
    qs = SocialApp.objects.filter(provider='google')
    if qs.count() > 1:
        qs.delete()
        qs = SocialApp.objects.none()
    SocialApp.objects.update_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': client_id,
            'secret': secret,
            'key': '',
        },
    )


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals  # noqa: F401

        post_migrate.connect(_sync_social_apps, sender=self)

        # Enable WAL journal mode on SQLite connections (dev only).
        # WAL allows concurrent reads during writes and avoids "database is locked".
        from django.db.backends.signals import connection_created

        def _set_sqlite_pragmas(sender, connection, **kwargs):
            if connection.vendor == 'sqlite':
                cursor = connection.cursor()
                cursor.execute('PRAGMA journal_mode=WAL;')
                cursor.execute('PRAGMA synchronous=NORMAL;')
                cursor.execute('PRAGMA cache_size=-8000;')   # 8 MB page cache
                cursor.execute('PRAGMA temp_store=MEMORY;')

        connection_created.connect(_set_sqlite_pragmas)