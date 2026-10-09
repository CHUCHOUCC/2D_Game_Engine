from psycopg.types.json import Jsonb

DEFAULT_DIFFICULTY = 0.5


class AiModelRepository:
    """What the AI learned per project ('ai_models', 'ai_training_samples') and
    a record of every AI call ('ai_requests', 'ai_generations')."""

    def __init__(self, connection):
        self._connection = connection

    def get(self, project_id: int) -> dict:
        """The model of a project; an empty one if it has not learned anything yet."""
        row = self._connection.execute(
            "select id, parameters, samples_seen, version from ai_models where project_id = %s", (project_id,)
        ).fetchone()
        if row is None:
            return {"id": None, "parameters": {}, "samples_seen": 0, "version": 0}
        return dict(row)

    def save(self, project_id: int, parameters: dict) -> int:
        """Store new parameters after one learning step; returns the model id."""
        row = self._connection.execute(
            "insert into ai_models (project_id, parameters, samples_seen) values (%s, %s, 1) "
            "on conflict (project_id) do update set parameters = excluded.parameters, "
            "samples_seen = ai_models.samples_seen + 1, version = ai_models.version + 1, updated_at = now() "
            "returning id",
            (project_id, Jsonb(parameters)),
        ).fetchone()
        return row["id"]

    def add_sample(self, model_id: int, play_id: int, features: dict, reward: float) -> None:
        self._connection.execute(
            "insert into ai_training_samples (ai_model_id, play_session_id, features, reward) "
            "values (%s, %s, %s, %s)",
            (model_id, play_id, Jsonb(features), reward),
        )

    def record_request(self, project_id: int, user_id: int, prompt: str, status: str,
                       error: str = "", duration_ms: int = 0) -> int:
        row = self._connection.execute(
            "insert into ai_requests (project_id, user_id, prompt, status, error, duration_ms) "
            "values (%s, %s, %s, %s, %s, %s) returning id",
            (project_id, user_id, prompt[:500], status, error[:300], duration_ms),
        ).fetchone()
        return row["id"]

    def record_generation(self, request_id: int, objects: list, difficulty: float) -> None:
        self._connection.execute(
            "insert into ai_generations (request_id, object_count, objects, difficulty) values (%s, %s, %s, %s)",
            (request_id, len(objects), Jsonb(objects), difficulty),
        )


def difficulty_of(model: dict) -> float:
    value = model.get("parameters", {}).get("difficulty", DEFAULT_DIFFICULTY)
    return float(value) if isinstance(value, (int, float)) else DEFAULT_DIFFICULTY
