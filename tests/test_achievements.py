from app.play.achievements import earned_codes
from app.play.schemas import RunResult

BASE = dict(outcome="lost", score=0, coins_collected=0, coins_total=5, enemies_defeated=0,
            damage_taken=3, deaths=1, duration_ms=1000)


def run(**changes):
    return RunResult(**{**BASE, **changes})


def test_a_bad_run_earns_nothing():
    assert earned_codes(run(), {}) == []


def test_any_coin_earns_first_coin():
    assert earned_codes(run(coins_collected=1), {}) == ["first-coin"]


def test_all_coins_earn_coin_hoarder():
    assert "coin-hoarder" in earned_codes(run(coins_collected=5), {})


def test_a_level_without_coins_never_gives_coin_hoarder():
    assert "coin-hoarder" not in earned_codes(run(coins_total=0), {})


def test_winning_without_damage_is_untouchable():
    assert earned_codes(run(outcome="won", damage_taken=0), {}) == ["first-win", "untouchable"]
    assert earned_codes(run(outcome="won"), {}) == ["first-win"]


def test_hunter_depends_on_the_player_totals():
    assert "hunter" not in earned_codes(run(), {"enemies_defeated": 9})
    assert "hunter" in earned_codes(run(), {"enemies_defeated": 10})
    assert "hunter" not in earned_codes(run(), None)
