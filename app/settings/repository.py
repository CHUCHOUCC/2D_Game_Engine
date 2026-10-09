DEFAULTS = {
    "theme": "dark",
    "language": "es",
    "show_grid": True,
    "snap_to_grid": True,
    "grid_size": 32,
    "music_volume": 70,
    "sfx_volume": 80,
}
_FIELDS = tuple(DEFAULTS)


class SettingsRepository:
    """The 'user_settings' table: one row per user, created on first save."""

    def __init__(self, connection):
        self._connection = connection

    def get(self, user_id: int) -> dict:
        row = self._connection.execute(
            f"select {', '.join(_FIELDS)} from user_settings where user_id = %s", (user_id,)
        ).fetchone()
        return dict(row) if row else dict(DEFAULTS)

    def save(self, user_id: int, settings: dict) -> dict:
        values = [settings[field] for field in _FIELDS]
        updates = ", ".join(f"{field} = excluded.{field}" for field in _FIELDS)
        row = self._connection.execute(
            f"insert into user_settings (user_id, {', '.join(_FIELDS)}) "
            f"values (%s, {', '.join(['%s'] * len(_FIELDS))}) "
            f"on conflict (user_id) do update set {updates}, updated_at = now() "
            f"returning {', '.join(_FIELDS)}",
            (user_id, *values),
        ).fetchone()
        return dict(row)
