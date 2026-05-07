from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _sync_social_apps(sender, **kwargs):
    """Sync SocialApp DB records from SOCIALACCOUNT_PROVIDERS settings.

    allauth 65.x uses the database SocialApp record over the settings APP config
    when a record exists. This keeps the DB record in sync with env-var credentials
    so a stale/empty DB record never blocks OAuth.
    """
    from django.conf import settings
    try:
        from allauth.socialaccount.models import SocialApp
    except Exception:
        return

    providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
    for provider_id, cfg in providers.items():
        app_cfg = cfg.get('APP', {})
        client_id = app_cfg.get('client_id', '')
        secret = app_cfg.get('secret', '')
        if not client_id:
            continue
        # Delete duplicates first so update_or_create won't raise MultipleObjectsReturned.
        qs = SocialApp.objects.filter(provider=provider_id)
        if qs.count() > 1:
            qs.delete()
        SocialApp.objects.update_or_create(
            provider=provider_id,
            defaults={
                'name': provider_id.capitalize(),
                'client_id': client_id,
                'secret': secret,
                'key': app_cfg.get('key', ''),
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