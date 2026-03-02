from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        from django.db.backends.signals import connection_created

        connection_created.connect(_set_wal_mode)


def _set_wal_mode(sender: object, connection: object, **kwargs: object) -> None:
    """Enable WAL journal mode for every new SQLite connection."""
    from django.db.backends.base.base import BaseDatabaseWrapper

    conn: BaseDatabaseWrapper = connection  # type: ignore[assignment]
    if conn.vendor == "sqlite":
        conn.connection.execute("PRAGMA journal_mode=WAL")  # type: ignore[union-attr]
