from fastapi.testclient import TestClient

from app.auth.dependencies import get_auth_service, get_commit
from app.main import app
from app.projects.router import get_repository
from tests.fakes import AuthFixture
from tests.test_projects import FakeProjectRepository

PASSWORD = "correct horse"


def make_client():
    """A client with the real routes, the real AuthService and in-memory repositories."""
    service = AuthFixture().service
    projects = FakeProjectRepository()
    app.dependency_overrides[get_auth_service] = lambda: service
    app.dependency_overrides[get_commit] = lambda: (lambda: None)
    app.dependency_overrides[get_repository] = lambda: projects
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def register(client, email="jesus@example.com", username="jesus", password=PASSWORD):
    return client.post("/auth/register", json={"username": username, "email": email, "password": password})


def log_in(client, email="jesus@example.com", password=PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(client, email="jesus@example.com"):
    register(client, email=email, username=email.split("@")[0])
    token = log_in(client, email=email).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_returns_201_and_hides_secrets():
    client = make_client()
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "jesus@example.com"
    assert set(body) == {"id", "username", "email"}


def test_register_twice_with_the_same_email_returns_409():
    client = make_client()
    register(client)
    assert register(client, username="other").status_code == 409


def test_register_validates_email_and_password():
    client = make_client()
    assert register(client, email="not-an-email").status_code == 422
    assert register(client, password="short").status_code == 422


def test_login_returns_a_bearer_token():
    client = make_client()
    register(client)
    response = log_in(client)
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert len(response.json()["access_token"]) >= 40


def test_login_with_a_wrong_password_and_with_an_unknown_email_look_the_same():
    client = make_client()
    register(client)
    wrong_password = log_in(client, password="wrong password")
    unknown_email = log_in(client, email="nobody@example.com")
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_me_returns_the_logged_in_user():
    client = make_client()
    headers = auth_header(client)
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "jesus@example.com"


def test_me_without_a_token_or_with_a_bad_token_returns_401():
    client = make_client()
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer nonsense"}).status_code == 401


def test_logout_invalidates_the_token():
    client = make_client()
    headers = auth_header(client)
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_projects_require_a_token():
    client = make_client()
    assert client.post("/projects", json={"name": "p"}).status_code == 401
    assert client.get("/projects").status_code == 401


def test_a_user_cannot_see_or_change_another_users_project():
    client = make_client()
    alice = auth_header(client, "alice@example.com")
    bob = auth_header(client, "bob@example.com")
    project_id = client.post("/projects", json={"name": "alice's game"}, headers=alice).json()["id"]

    assert client.get(f"/projects/{project_id}", headers=alice).status_code == 200
    assert client.get(f"/projects/{project_id}", headers=bob).status_code == 404
    assert client.put(f"/projects/{project_id}/scene", json={"scene": []}, headers=bob).status_code == 404
    assert client.get("/projects", headers=bob).json() == []


def test_login_returns_a_refresh_token_and_its_lifetime():
    client = make_client()
    register(client)
    body = log_in(client).json()
    assert set(body) == {"access_token", "refresh_token", "token_type", "expires_in"}
    assert body["expires_in"] == 900


def test_refresh_returns_a_new_working_pair():
    client = make_client()
    register(client)
    first = log_in(client).json()
    response = client.post("/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert response.status_code == 200
    second = response.json()
    assert second["refresh_token"] != first["refresh_token"]
    me = client.get("/auth/me", headers={"Authorization": "Bearer " + second["access_token"]})
    assert me.status_code == 200


def test_refresh_with_a_bad_token_returns_401():
    client = make_client()
    assert client.post("/auth/refresh", json={"refresh_token": "nope"}).status_code == 401


def test_logout_with_the_refresh_token_revokes_it():
    client = make_client()
    register(client)
    pair = log_in(client).json()
    headers = {"Authorization": "Bearer " + pair["access_token"]}
    client.post("/auth/logout", json={"refresh_token": pair["refresh_token"]}, headers=headers)
    assert client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]}).status_code == 401


def test_logout_all_needs_a_token_and_returns_204():
    client = make_client()
    assert client.post("/auth/logout-all").status_code == 401
    assert client.post("/auth/logout-all", headers=auth_header(client)).status_code == 204


def test_repeated_failed_logins_return_429():
    client = make_client()
    register(client)
    for _ in range(5):
        assert log_in(client, password="wrong password").status_code == 401
    assert log_in(client).status_code == 429


def test_register_rejects_a_blank_username():
    client = make_client()
    assert register(client, username="   ").status_code == 422
