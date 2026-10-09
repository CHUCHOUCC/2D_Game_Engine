class LoginAttemptRepository:
    """The 'login_attempts' table, used to lock out password guessing."""

    def __init__(self, connection):
        self._connection = connection

    def record(self, email: str, ip_address: str, succeeded: bool) -> None:
        self._connection.execute(
            "insert into login_attempts (email, ip_address, succeeded) values (%s, %s, %s)",
            (email, ip_address, succeeded),
        )

    def failures_since(self, email: str, since) -> int:
        row = self._connection.execute(
            "select count(*) as n from login_attempts "
            "where email = %s and succeeded = false and attempted_at >= %s",
            (email, since),
        ).fetchone()
        return row["n"]

    def failures_from_ip_since(self, ip_address: str, since) -> int:
        row = self._connection.execute(
            "select count(*) as n from login_attempts "
            "where ip_address = %s and succeeded = false and attempted_at >= %s",
            (ip_address, since),
        ).fetchone()
        return row["n"]
