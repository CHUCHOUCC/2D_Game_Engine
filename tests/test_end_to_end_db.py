"""The whole API against a real PostgreSQL: no fakes, only the AI service is replaced.

Needs TEST_DATABASE_URL (a throw-away database with the migrations applied).
Unlike the repository tests, these requests commit, so every run uses a fresh email.
"""
import os
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai_learning.dependencies import get_optional_ai_client
from app.main import app
from app.projects.router import get_ai_client
from tests.fakes_game import FakeLearningAi

DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(DATABASE_URL is None, reason="TEST_DATABASE_URL is not set")

PASSWORD = "correct horse battery"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("JWT_SECRET", "end-to-end-secret-that-is-long-enough")
    ai = FakeLearningAi()
    app.dependency_overrides[get_ai_client] = lambda: ai
    app.dependency_overrides[get_optional_ai_client] = lambda: ai
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_register_play_learn_and_log_out(client):
    email = f"e2e-{uuid.uuid4().hex[:10]}@example.com"
    assert client.post("/auth/register", json={"username": "e2e", "email": email, "password": PASSWORD}).status_code == 201
    pair = client.post("/auth/login", json={"email": email, "password": PASSWORD}).json()
    headers = {"Authorization": f"Bearer {pair['access_token']}"}

    project = client.post("/projects", json={"name": "Aldea", "template": "village"}, headers=headers).json()
    assert len(project["scene"]) == 6
    scene = project["scene"] + [{"id": "hero", "kind": "player", "x": 64, "y": 64}]
    assert client.put(f"/projects/{project['id']}/scene", json={"scene": scene}, headers=headers).status_code == 200

    run = client.post(f"/projects/{project['id']}/plays", headers=headers).json()
    result = {"outcome": "won", "score": 90, "coins_collected": 2, "coins_total": 2, "enemies_defeated": 1,
              "damage_taken": 0, "deaths": 0, "duration_ms": 30000, "events": []}
    finished = client.post(f"/projects/{project['id']}/plays/{run['id']}/finish", json=result, headers=headers).json()
    assert finished["learned"] is True
    assert "untouchable" in finished["achievements"]

    obstacles = client.post(f"/projects/{project['id']}/ai/obstacles", json={"count": 2}, headers=headers).json()
    assert obstacles["added"] == 2
    assert client.get(f"/projects/{project['id']}/ai/model", headers=headers).json()["samples_seen"] == 1
    assert client.get("/me/stats", headers=headers).json()["games_won"] == 1
    assert len(client.get(f"/projects/{project['id']}/versions", headers=headers).json()) == 1

    refreshed = client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]}).json()
    new_headers = {"Authorization": f"Bearer {refreshed['access_token']}"}
    assert client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]}).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": refreshed["refresh_token"]}).status_code == 401

    assert client.post("/auth/logout", headers=new_headers).status_code == 204
    assert client.get("/auth/me", headers=new_headers).status_code == 401
    actions = [a["action"] for a in client.get("/me/activity", headers=headers).json()]
    assert actions[0] == "user.logout"
    assert "token.reuse_detected" in actions


def test_settings_and_profile_are_stored(client):
    email = f"e2e-{uuid.uuid4().hex[:10]}@example.com"
    client.post("/auth/register", json={"username": "e2e", "email": email, "password": PASSWORD})
    token = client.post("/auth/login", json={"email": email, "password": PASSWORD}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.put("/me/settings", json={"theme": "light", "language": "en"}, headers=headers)
    assert client.get("/me/settings", headers=headers).json()["theme"] == "light"
    client.put("/me/profile", json={"display_name": "Chucho"}, headers=headers)
    assert client.get("/me/profile", headers=headers).json()["display_name"] == "Chucho"
    kinds = [k["code"] for k in client.get("/catalog/kinds", headers=headers).json()]
    assert "house" in kinds


def test_failed_logins_survive_the_error_response_and_lock_the_account(client):
    email = f"e2e-{uuid.uuid4().hex[:10]}@example.com"
    client.post("/auth/register", json={"username": "e2e", "email": email, "password": PASSWORD})
    for _ in range(5):
        assert client.post("/auth/login", json={"email": email, "password": "wrong password"}).status_code == 401
    assert client.post("/auth/login", json={"email": email, "password": PASSWORD}).status_code == 429
