from psycopg.types.json import Jsonb


class AuditLog:
    """Writes one row in 'audit_logs' per important action."""

    def __init__(self, connection):
        self._connection = connection

    def record(self, user_id, action: str, entity_type: str = "", entity_id="", details=None,
               ip_address: str = "") -> None:
        self._connection.execute(
            "insert into audit_logs (user_id, action, entity_type, entity_id, details, ip_address) "
            "values (%s, %s, %s, %s, %s, %s)",
            (user_id, action, entity_type, str(entity_id), Jsonb(details or {}), ip_address),
        )

    def recent_for_user(self, user_id: int, limit: int = 50) -> list:
        return self._connection.execute(
            "select action, entity_type, entity_id, details, created_at from audit_logs "
            "where user_id = %s order by created_at desc limit %s",
            (user_id, limit),
        ).fetchall()
