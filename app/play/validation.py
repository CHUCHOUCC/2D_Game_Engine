"""Checks a finished run against the level it was played on.

The game runs in the browser, so whatever it sends could have been typed by
hand. These rules only accept numbers the saved scene can really produce; they
protect the leaderboard, the achievements and the AI that learns from runs.
"""
from app.projects.world import COIN_POINTS, ENEMY_KINDS, ENEMY_POINTS

from .schemas import RunResult


class ImplausibleRunError(ValueError):
    """The run claims something the level cannot give."""


def check_run(run: RunResult, scene: list) -> None:
    """Raise ImplausibleRunError if the run does not fit the scene."""
    coins = sum(1 for obj in scene if obj.get("kind") == "coin")
    enemy_points = sorted(
        (ENEMY_POINTS.get(obj.get("kind"), 0) for obj in scene if obj.get("kind") in ENEMY_KINDS),
        reverse=True,
    )
    if run.coins_total != coins:
        raise ImplausibleRunError("coins_total does not match the level")
    if run.enemies_defeated > len(enemy_points):
        raise ImplausibleRunError("more enemies defeated than the level has")
    # Best case: every coin taken and the most valuable enemies defeated.
    best_score = run.coins_collected * COIN_POINTS + sum(enemy_points[: run.enemies_defeated])
    if run.score > best_score:
        raise ImplausibleRunError("score is higher than the run allows")
    if run.outcome == "won" and not _is_win(run, coins, len(enemy_points)):
        raise ImplausibleRunError("the run does not meet the goal of the level")


def _is_win(run: RunResult, coins: int, enemies: int) -> bool:
    """Same rule as the game: every coin; a level without coins, every enemy."""
    if coins > 0:
        return run.coins_collected == coins
    return enemies > 0 and run.enemies_defeated == enemies
