from fastapi.testclient import TestClient

from app.ai_learning.dependencies import get_ai_models, get_optional_ai_client
from app.auth.dependencies import current_user
from app.auth.user import User
from app.main import app
from app.play.router import get_achievements, get_plays
from app.projects.router import get_ai_client, get_repository
from tests.fakes_game import FakeAchievementRepository, FakeAiModelRepository, FakeLearningAi, FakePlayRepository
from tests.test_projects import FakeProjectRepository

RUN = {
    "outcome": "won", "score": 120, "coins_collected": 5, "coins_total": 6,
    "enemies_defeated": 2, "damage_taken": 1, "deaths": 0, "duration_ms": 45000,
    "events": [{"kind": "coin", "x": 10, "y": 20, "at_ms": 1000}],
}


class World:
    def __init__(self, ai=None, user_id=1):
        self.projects = FakeProjectRepository()
        self.plays = FakePlayRepository()
        self.models = FakeAiModelRepository()
        self.achievements = FakeAchievementRepository()
        app.dependency_overrides[get_achievements] = lambda: self.achievements
        self.ai = ai
        self.user = User(user_id, "jesus", "j@example.com", b"s", b"h")
        app.dependency_overrides[get_repository] = lambda: self.projects
        app.dependency_overrides[get_plays] = lambda: self.plays
        app.dependency_overrides[get_ai_models] = lambda: self.models
        app.dependency_overrides[get_optional_ai_client] = lambda: self.ai
        app.dependency_overrides[get_ai_client] = lambda: self.ai
        app.dependency_overrides[current_user] = lambda: self.user
        self.client = TestClient(app)
        self.project_id = self.projects.create(user_id, "level", [{"id": "c", "kind": "coin", "x": 5, "y": 5}]).id


def teardown_function():
    app.dependency_overrides.clear()


def play(world, run=RUN):
    run_id = world.client.post(f"/projects/{world.project_id}/plays").json()["id"]
    return world.client.post(f"/projects/{world.project_id}/plays/{run_id}/finish", json=run)


def test_start_run_returns_an_id_and_the_default_difficulty():
    world = World()
    response = world.client.post(f"/projects/{world.project_id}/plays")
    assert response.status_code == 201
    assert response.json() == {"id": 1, "difficulty": 0.5}


def test_finish_run_without_ai_still_saves_everything():
    world = World(ai=None)
    response = play(world)
    assert response.status_code == 200
    assert response.json()["learned"] is False
    assert response.json()["difficulty"] == 0.5
    assert world.plays.runs[1]["result"].score == 120
    assert world.plays.stats[1]["games_played"] == 1
    assert world.plays.scores == [(world.project_id, 1, 120)]


def test_finish_run_lets_the_ai_learn_and_raises_difficulty_after_a_win():
    world = World(ai=FakeLearningAi())
    body = play(world).json()
    assert body["learned"] is True
    assert round(body["difficulty"], 2) == 0.6
    assert world.models.get(world.project_id)["samples_seen"] == 1
    assert world.ai.learned[0][1]["outcome"] == "won"
    assert "events" not in world.ai.learned[0][1]
    next_run = world.client.post(f"/projects/{world.project_id}/plays").json()
    assert round(next_run["difficulty"], 2) == 0.6


def test_ai_failure_does_not_lose_the_run():
    world = World(ai=FakeLearningAi(fail=True))
    response = play(world)
    assert response.status_code == 200
    assert response.json()["learned"] is False
    assert world.plays.runs[1]["result"] is not None


def test_a_run_cannot_be_finished_twice():
    world = World()
    run_id = world.client.post(f"/projects/{world.project_id}/plays").json()["id"]
    url = f"/projects/{world.project_id}/plays/{run_id}/finish"
    assert world.client.post(url, json=RUN).status_code == 200
    assert world.client.post(url, json=RUN).status_code == 404


def test_invalid_run_numbers_are_rejected():
    world = World()
    run_id = world.client.post(f"/projects/{world.project_id}/plays").json()["id"]
    url = f"/projects/{world.project_id}/plays/{run_id}/finish"
    assert world.client.post(url, json={**RUN, "coins_collected": 9}).status_code == 422
    assert world.client.post(url, json={**RUN, "outcome": "draw"}).status_code == 422
    assert world.client.post(url, json={**RUN, "score": -1}).status_code == 422


def test_another_users_project_cannot_be_played():
    world = World()
    other = world.projects.create(2, "not mine", []).id
    assert world.client.post(f"/projects/{other}/plays").status_code == 404
    assert world.client.get(f"/projects/{other}/leaderboard").status_code == 404


def test_leaderboard_and_my_stats():
    world = World()
    play(world)
    play(world, {**RUN, "score": 300})
    board = world.client.get(f"/projects/{world.project_id}/leaderboard").json()
    assert [row["score"] for row in board] == [300, 120]
    assert world.client.get("/me/stats").json()["best_score"] == 300


def test_my_stats_before_playing_are_zero():
    assert World().client.get("/me/stats").json()["games_played"] == 0


def test_learned_obstacles_are_added_to_the_scene():
    world = World(ai=FakeLearningAi())
    response = world.client.post(f"/projects/{world.project_id}/ai/obstacles", json={"count": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["added"] == 3
    assert [obj["kind"] for obj in body["scene"]] == ["coin", "wall", "wall", "wall"]
    assert world.models.requests == [(world.project_id, "obstacles:3", "ok")]
    assert world.models.generations[0][1] == 3


def test_obstacle_count_is_limited():
    world = World(ai=FakeLearningAi())
    url = f"/projects/{world.project_id}/ai/obstacles"
    assert world.client.post(url, json={"count": 0}).status_code == 422
    assert world.client.post(url, json={"count": 31}).status_code == 422


def test_obstacles_when_the_ai_is_down_return_502():
    world = World(ai=FakeLearningAi(fail=True))
    response = world.client.post(f"/projects/{world.project_id}/ai/obstacles", json={"count": 2})
    assert response.status_code == 502


def test_model_endpoint_shows_what_was_learned():
    world = World(ai=FakeLearningAi())
    assert world.client.get(f"/projects/{world.project_id}/ai/model").json()["samples_seen"] == 0
    play(world)
    model = world.client.get(f"/projects/{world.project_id}/ai/model").json()
    assert model["samples_seen"] == 1
    assert round(model["difficulty"], 2) == 0.6


def test_finishing_runs_unlocks_achievements_once():
    world = World()
    first = play(world).json()["achievements"]
    assert first == ["first-coin", "first-win"]
    perfect = {**RUN, "coins_collected": 6, "damage_taken": 0}
    assert play(world, perfect).json()["achievements"] == ["coin-hoarder", "untouchable"]
    assert play(world, perfect).json()["achievements"] == []
    codes = [a["code"] for a in world.client.get("/me/achievements").json()]
    assert codes == ["first-coin", "first-win", "coin-hoarder", "untouchable"]
