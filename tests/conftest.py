import pytest

from app.main import app


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Every test starts with empty rate-limit counters (they are per process)."""
    app.state.rate_limiter.reset()
    yield
    app.state.rate_limiter.reset()
