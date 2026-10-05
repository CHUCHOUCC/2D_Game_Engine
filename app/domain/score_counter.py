from .event import Event


class ScoreCounter:
    """Keeps the score and applies the rule of each event.

    Rules: a coin adds 10, damage subtracts 5, the score never drops below
    zero, and an unknown event leaves the state unchanged.
    """

    KIND_COIN = "coin"
    KIND_DAMAGE = "damage"
    COIN_POINTS = 10
    DAMAGE_POINTS = 5

    def __init__(self):
        self._score = 0

    @property
    def score(self):
        return self._score

    def apply(self, event: Event):
        """Apply an event and return a message describing the result."""
        if event.kind == self.KIND_COIN:
            self._score += self.COIN_POINTS
            return f"Coin: score {self._score}"
        if event.kind == self.KIND_DAMAGE:
            self._score = max(0, self._score - self.DAMAGE_POINTS)
            return f"Damage: score {self._score}"
        return f"Unknown event '{event.kind}': score unchanged ({self._score})"
