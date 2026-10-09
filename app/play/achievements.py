"""Which achievements a finished run unlocks.

The rules are plain functions of the run and the player's totals, so they are
easy to test; the repository only stores the result.
"""
from .schemas import RunResult

HUNTER_TARGET = 10


def earned_codes(run: RunResult, totals: dict | None) -> list:
    """Achievement codes this run earns (the repository ignores ones already owned).

    totals are the player's stats *after* this run was added.
    """
    totals = totals or {}
    codes = []
    if run.coins_collected > 0:
        codes.append("first-coin")
    if run.coins_total > 0 and run.coins_collected == run.coins_total:
        codes.append("coin-hoarder")
    if run.outcome == "won":
        codes.append("first-win")
        if run.damage_taken == 0:
            codes.append("untouchable")
    if totals.get("enemies_defeated", 0) >= HUNTER_TARGET:
        codes.append("hunter")
    return codes


class AchievementRepository:
    """'achievements' and 'user_achievements'."""

    def __init__(self, connection):
        self._connection = connection

    def unlock(self, user_id: int, codes: list) -> list:
        """Unlock the given codes and return only the ones that are new."""
        if not codes:
            return []
        rows = self._connection.execute(
            "insert into user_achievements (user_id, achievement_id) "
            "select %s, id from achievements where code = any(%s) "
            "on conflict do nothing returning achievement_id",
            (user_id, codes),
        ).fetchall()
        if not rows:
            return []
        new = self._connection.execute(
            "select code from achievements where id = any(%s) order by id",
            ([row["achievement_id"] for row in rows],),
        ).fetchall()
        return [row["code"] for row in new]

    def of_user(self, user_id: int) -> list:
        return self._connection.execute(
            "select a.code, a.name, a.description, a.points, ua.unlocked_at "
            "from user_achievements ua join achievements a on a.id = ua.achievement_id "
            "where ua.user_id = %s order by ua.unlocked_at",
            (user_id,),
        ).fetchall()
