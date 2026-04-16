from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'


    def ready(self):
        import core.signals  # noqa: F401

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