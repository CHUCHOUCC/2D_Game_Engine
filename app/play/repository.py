from psycopg.types.json import Jsonb

from .schemas import RunResult


class PlayRepository:
    """Runs of the game: 'play_sessions', 'play_events', 'player_stats' and 'high_scores'."""

    def __init__(self, connection):
        self._connection = connection

    def start(self, project_id: int, player_id: int, difficulty: float) -> int:
        row = self._connection.execute(
            "insert into play_sessions (project_id, player_id, difficulty) values (%s, %s, %s) returning id",
            (project_id, player_id, difficulty),
        ).fetchone()
        return row["id"]

    def find_open(self, play_id: int, project_id: int, player_id: int):
        """A run that belongs to this player and project and has not ended yet."""
        return self._connection.execute(
            "select id, difficulty from play_sessions "
            "where id = %s and project_id = %s and player_id = %s and ended_at is null",
            (play_id, project_id, player_id),
        ).fetchone()

    def finish(self, play_id: int, result: RunResult) -> None:
        self._connection.execute(
            "update play_sessions set ended_at = now(), outcome = %s, score = %s, coins_collected = %s, "
            "coins_total = %s, enemies_defeated = %s, damage_taken = %s, deaths = %s, duration_ms = %s "
            "where id = %s",
            (result.outcome, result.score, result.coins_collected, result.coins_total,
             result.enemies_defeated, result.damage_taken, result.deaths, result.duration_ms, play_id),
        )
        with self._connection.cursor() as cursor:
            cursor.executemany(
                "insert into play_events (play_session_id, kind, x, y, at_ms) values (%s, %s, %s, %s, %s)",
                [(play_id, e.kind, e.x, e.y, e.at_ms) for e in result.events],
            )

    def add_to_player_stats(self, user_id: int, result: RunResult) -> None:
        won = 1 if result.outcome == "won" else 0
        self._connection.execute(
            "insert into player_stats (user_id, games_played, games_won, total_score, best_score, "
            "coins_collected, enemies_defeated, deaths, play_time_ms) "
            "values (%s, 1, %s, %s, %s, %s, %s, %s, %s) "
            "on conflict (user_id) do update set "
            "games_played = player_stats.games_played + 1, "
            "games_won = player_stats.games_won + excluded.games_won, "
            "total_score = player_stats.total_score + excluded.total_score, "
            "best_score = greatest(player_stats.best_score, excluded.best_score), "
            "coins_collected = player_stats.coins_collected + excluded.coins_collected, "
            "enemies_defeated = player_stats.enemies_defeated + excluded.enemies_defeated, "
            "deaths = player_stats.deaths + excluded.deaths, "
            "play_time_ms = player_stats.play_time_ms + excluded.play_time_ms, "
            "updated_at = now()",
            (user_id, won, result.score, result.score, result.coins_collected,
             result.enemies_defeated, result.deaths, result.duration_ms),
        )

    def add_high_score(self, project_id: int, user_id: int, score: int) -> None:
        self._connection.execute(
            "insert into high_scores (project_id, user_id, score) values (%s, %s, %s)",
            (project_id, user_id, score),
        )

    def leaderboard(self, project_id: int, limit: int = 10) -> list:
        return self._connection.execute(
            "select u.username, max(h.score) as score from high_scores h "
            "join users u on u.id = h.user_id where h.project_id = %s "
            "group by u.username order by score desc limit %s",
            (project_id, limit),
        ).fetchall()

    def stats_of(self, user_id: int):
        return self._connection.execute(
            "select games_played, games_won, total_score, best_score, coins_collected, "
            "enemies_defeated, deaths, play_time_ms from player_stats where user_id = %s",
            (user_id,),
        ).fetchone()

    def record_event_summary(self, play_id: int, details: dict) -> None:
        """Attach a summary event (e.g. what the AI learned) to the run."""
        self._connection.execute(
            "insert into play_events (play_session_id, kind, details) values (%s, 'summary', %s)",
            (play_id, Jsonb(details)),
        )
