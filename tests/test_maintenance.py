from app.maintenance import purge


class RecordingConnection:
    def __init__(self):
        self.sql = []
        self.committed = False

    def execute(self, sql):
        self.sql.append(sql)

        class Cursor:
            rowcount = 2
        return Cursor()

    def commit(self):
        self.committed = True


def test_purge_cleans_every_login_table_and_commits():
    connection = RecordingConnection()
    counts = purge(connection)
    assert counts == {"revoked_access_tokens": 2, "refresh_tokens": 2, "login_attempts": 2, "sessions": 2}
    assert all(sql.startswith("delete from") for sql in connection.sql)
    assert connection.committed
