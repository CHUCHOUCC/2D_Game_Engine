from fastapi.testclient import TestClient

from app.auth.dependencies import current_user
from app.auth.user import User
from app.main import app
from app.settings.router import get_settings_repository
from tests.fakes_game import FakeSettingsRepository


def make_client():
    repo = FakeSettingsRepository()
    app.dependency_overrides[get_settings_repository] = lambda: repo
    app.dependency_overrides[current_user] = lambda: User(1, "j", "j@example.com", b"s", b"h")
    return TestClient(app), repo


def teardown_function():
    app.dependency_overrides.clear()


def test_settings_start_with_dark_theme_and_spanish():
    client, _ = make_client()
    body = client.get("/me/settings").json()
    assert body["theme"] == "dark"
    assert body["language"] == "es"


def test_save_and_read_settings():
    client, _ = make_client()
    saved = client.put("/me/settings", json={"theme": "light", "grid_size": 16, "sfx_volume": 0})
    assert saved.status_code == 200
    body = client.get("/me/settings").json()
    assert (body["theme"], body["grid_size"], body["sfx_volume"]) == ("light", 16, 0)


def test_invalid_settings_are_rejected():
    client, _ = make_client()
    assert client.put("/me/settings", json={"theme": "purple"}).status_code == 422
    assert client.put("/me/settings", json={"grid_size": 4}).status_code == 422
    assert client.put("/me/settings", json={"music_volume": 101}).status_code == 422


def test_settings_need_a_token():
    client, _ = make_client()
    del app.dependency_overrides[current_user]
    assert client.get("/me/settings").status_code == 401


def test_settings_are_read_from_the_database_once_and_updated_on_save():
    client, repo = make_client()
    calls = {"n": 0}
    original = repo.get

    def counting(user_id):
        calls["n"] += 1
        return original(user_id)

    repo.get = counting
    client.get("/me/settings")
    client.get("/me/settings")
    assert calls["n"] == 1
    client.put("/me/settings", json={"theme": "light"})
    # Write-through: the next read already sees the change, without a new query.
    assert client.get("/me/settings").json()["theme"] == "light"
    assert calls["n"] == 1


def test_each_user_has_their_own_cached_settings():
    client, _ = make_client()
    client.put("/me/settings", json={"theme": "light"})
    app.dependency_overrides[current_user] = lambda: User(2, "k", "k@example.com", b"s", b"h")
    assert client.get("/me/settings").json()["theme"] == "dark"
