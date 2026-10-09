from fastapi.testclient import TestClient

from app.ai_client import AiServiceError
from app.main import app
from app.projects.router import current_owner_id, get_ai_client, get_repository
from tests.test_projects import FakeProjectRepository


class FakeAiClient:
    def __init__(self, objects=None, error=None):
        self._objects = objects
        self._error = error
        self.prompts = []

    def generate(self, prompt, scene=None):
        self.prompts.append(prompt)
        if self._error:
            raise self._error
        return self._objects


def make_client(ai_client, owner_id=1, repo=None):
    repo = repo or FakeProjectRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[current_owner_id] = lambda: owner_id
    app.dependency_overrides[get_ai_client] = lambda: ai_client
    return TestClient(app), repo


def teardown_function():
    app.dependency_overrides.clear()


def test_ai_objects_are_added_to_the_scene():
    ai = FakeAiClient([{"id": "coin-1", "kind": "coin", "x": 10, "y": 20}])
    client, _ = make_client(ai)
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]

    response = client.post(f"/projects/{project_id}/ai", json={"prompt": "a coin at 10 20"})

    assert response.status_code == 200
    assert response.json()["scene"] == [{"id": "coin-1", "kind": "coin", "x": 10.0, "y": 20.0}]
    assert ai.prompts == ["a coin at 10 20"]


def test_new_objects_never_reuse_an_existing_id():
    ai = FakeAiClient([{"id": "coin-1", "kind": "coin", "x": 1, "y": 1}])
    client, _ = make_client(ai)
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]

    client.post(f"/projects/{project_id}/ai", json={"prompt": "a coin"})
    scene = client.post(f"/projects/{project_id}/ai", json={"prompt": "a coin"}).json()["scene"]

    assert [obj["id"] for obj in scene] == ["coin-1", "coin-1-2"]


def test_ai_service_failure_returns_502_and_keeps_the_scene():
    client, _ = make_client(FakeAiClient(error=AiServiceError("down")))
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]

    response = client.post(f"/projects/{project_id}/ai", json={"prompt": "a coin"})

    assert response.status_code == 502
    assert client.get(f"/projects/{project_id}").json()["scene"] == []


def test_invalid_objects_from_the_ai_service_are_rejected():
    client, _ = make_client(FakeAiClient([{"id": "a", "kind": "box", "x": "oops", "y": 1}]))
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]
    assert client.post(f"/projects/{project_id}/ai", json={"prompt": "x"}).status_code == 502


def test_other_owner_cannot_use_ai_on_a_project():
    ai = FakeAiClient([{"id": "a", "kind": "box", "x": 1, "y": 1}])
    client_a, repo = make_client(ai, owner_id=1)
    project_id = client_a.post("/projects", json={"name": "p"}).json()["id"]

    client_b, _ = make_client(ai, owner_id=2, repo=repo)
    assert client_b.post(f"/projects/{project_id}/ai", json={"prompt": "x"}).status_code == 404
    assert ai.prompts == []


def test_missing_configuration_returns_503(monkeypatch):
    monkeypatch.delenv("AI_SERVICE_URL", raising=False)
    monkeypatch.delenv("AI_SERVICE_KEY", raising=False)
    repo = FakeProjectRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[current_owner_id] = lambda: 1
    client = TestClient(app)
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]
    assert client.post(f"/projects/{project_id}/ai", json={"prompt": "x"}).status_code == 503


def test_ai_cannot_add_a_second_player():
    ai = FakeAiClient([{"id": "p", "kind": "player", "x": 1, "y": 1}, {"id": "w", "kind": "wall", "x": 5, "y": 5}])
    client, _ = make_client(ai)
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]
    scene = client.post(f"/projects/{project_id}/ai", json={"prompt": "x"}).json()["scene"]
    assert [obj["kind"] for obj in scene] == ["wall"]


def test_ai_objects_outside_the_world_are_rejected():
    client, _ = make_client(FakeAiClient([{"id": "a", "kind": "box", "x": 99999, "y": 1}]))
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]
    assert client.post(f"/projects/{project_id}/ai", json={"prompt": "x"}).status_code == 502
