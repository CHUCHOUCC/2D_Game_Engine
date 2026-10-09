from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.auth.dependencies import current_user
from app.auth.user import User
from app.main import app
from app.profile.router import get_audit_log, get_profiles


class FakeProfiles:
    def __init__(self):
        self.rows = {}

    def get(self, user_id):
        return self.rows.get(user_id, {"display_name": "", "avatar_url": "", "bio": "", "country": ""})

    def save(self, user_id, profile):
        self.rows[user_id] = profile
        return profile


class FakeAudit:
    def recent_for_user(self, user_id, limit=50):
        return [{"action": "user.login", "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc)}]


def make_client():
    profiles = FakeProfiles()
    app.dependency_overrides[get_profiles] = lambda: profiles
    app.dependency_overrides[get_audit_log] = FakeAudit
    app.dependency_overrides[current_user] = lambda: User(1, "jesus", "j@example.com", b"s", b"h")
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_profile_starts_empty_but_has_the_account_data():
    body = make_client().get("/me/profile").json()
    assert body["username"] == "jesus"
    assert body["display_name"] == ""


def test_save_profile():
    client = make_client()
    saved = client.put("/me/profile", json={"display_name": "Chucho", "country": "CO"})
    assert saved.status_code == 200
    assert client.get("/me/profile").json()["display_name"] == "Chucho"


def test_avatar_must_be_https_and_bio_is_limited():
    client = make_client()
    assert client.put("/me/profile", json={"avatar_url": "javascript:alert(1)"}).status_code == 422
    assert client.put("/me/profile", json={"avatar_url": "http://x.com/a.png"}).status_code == 422
    assert client.put("/me/profile", json={"bio": "x" * 501}).status_code == 422
    assert client.put("/me/profile", json={"avatar_url": "https://x.com/a.png"}).status_code == 200


def test_activity_lists_recent_security_events():
    assert make_client().get("/me/activity").json() == [
        {"action": "user.login", "created_at": "2026-01-01T00:00:00+00:00"}
    ]
