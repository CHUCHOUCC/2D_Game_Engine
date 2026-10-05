from app.domain import Event, ScoreCounter

COIN = Event("coin")
DAMAGE = Event("damage")


def process(events):
    """Process events one by one and return the score after each one."""
    counter = ScoreCounter()
    return [(counter.apply(e), counter.score)[1] for e in events]


def test_coin_coin_damage_gives_10_20_15():
    assert process([COIN, COIN, DAMAGE]) == [10, 20, 15]


def test_damage_from_zero_stays_at_zero():
    assert process([DAMAGE]) == [0]


def test_empty_list_keeps_zero():
    assert process([]) == []
    assert ScoreCounter().score == 0


def test_unknown_event_keeps_the_previous_score():
    counter = ScoreCounter()
    counter.apply(COIN)
    message = counter.apply(Event("teleport"))
    assert counter.score == 10
    assert "Unknown" in message
