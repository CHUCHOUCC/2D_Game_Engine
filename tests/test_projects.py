from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.projects.project import Project
from app.projects.router import current_owner_id, get_repository


class FakeProjectRepository:
    """In-memory stand-in with the same interface, so the API is tested without a database."""

    def __init__(self):
        self._projects = {}
        self._next_id = 1

    def create(self, owner_id, name, scene):
        project = Project(self._next_id, owner_id, name, scene, datetime.now(timezone.utc))
        self._projects[project.id] = project
        self._next_id += 1
        return project

    def list_by_owner(self, owner_id):
        return [p for p in self._projects.values() if p.owner_id == owner_id]

    def find_by_id(self, project_id, owner_id):
        project = self._projects.get(project_id)
        return project if project and project.owner_id == owner_id else None

    def update_scene(self, project_id, owner_id, scene):
        project = self.find_by_id(project_id, owner_id)
        if project is None:
            return None
        updated = Project(project.id, owner_id, project.name, scene, datetime.now(timezone.utc))
        self._projects[project_id] = updated
        return updated


def make_client(owner_id=1, repo=None):
    repo = repo or FakeProjectRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[current_owner_id] = lambda: owner_id
    return TestClient(app), repo


def teardown_function():
    app.dependency_overrides.clear()


def test_create_project_returns_201_with_empty_scene():
    client, _ = make_client()
    response = client.post("/projects", json={"name": "level 1"})
    assert response.status_code == 201
    assert response.json()["name"] == "level 1"
    assert response.json()["scene"] == []


def test_save_and_load_scene_round_trip():
    client, _ = make_client()
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]
    scene = [{"id": "a", "kind": "box", "x": 10.5, "y": 20.0}]

    saved = client.put(f"/projects/{project_id}/scene", json={"scene": scene})
    assert saved.status_code == 200

    loaded = client.get(f"/projects/{project_id}")
    assert loaded.json()["scene"] == scene


def test_list_returns_only_own_projects():
    client, repo = make_client(owner_id=1)
    repo.create(2, "someone else's", [])
    client.post("/projects", json={"name": "mine"})
    names = [p["name"] for p in client.get("/projects").json()]
    assert names == ["mine"]


def test_other_owner_cannot_read_or_write_a_project():
    client_a, repo = make_client(owner_id=1)
    project_id = client_a.post("/projects", json={"name": "private"}).json()["id"]

    client_b, _ = make_client(owner_id=2, repo=repo)
    assert client_b.get(f"/projects/{project_id}").status_code == 404
    assert client_b.put(f"/projects/{project_id}/scene", json={"scene": []}).status_code == 404


def test_invalid_scene_object_is_rejected():
    client, _ = make_client()
    project_id = client.post("/projects", json={"name": "p"}).json()["id"]
    bad = [{"id": "a", "kind": "box", "x": "not a number", "y": 0}]
    assert client.put(f"/projects/{project_id}/scene", json={"scene": bad}).status_code == 422


def test_missing_project_returns_404():
    client, _ = make_client()
    assert client.get("/projects/999").status_code == 404
