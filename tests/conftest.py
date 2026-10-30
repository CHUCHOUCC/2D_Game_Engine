import pytest

from app.main import app


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Every test starts with empty rate-limit counters (they are per process)."""
    app.state.rate_limiter.reset()
    yield
    app.state.rate_limiter.reset()


@pytest.fixture(autouse=True)
def fresh_caches():
    """Every test starts with empty caches, so cached answers never leak between tests."""
    from app import cache

    cache.clear_all()
    yield
    cache.clear_all()
