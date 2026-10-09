import time

from fastapi import APIRouter, Depends, HTTPException

from app.ai_client import AiServiceClient, AiServiceError
from app.auth.dependencies import current_user
from app.auth.user import User
from app.projects.router import (
    append_objects,
    get_ai_client,
    get_repository,
    load_project,
    project_json,
    validate_generated,
)
from app.projects.schemas import ObstacleRequest
from .dependencies import get_ai_models
from .repository import AiModelRepository, difficulty_of

router = APIRouter(prefix="/projects/{project_id}/ai", tags=["ai"])


@router.get("/model")
def get_model(project_id: int, repo=Depends(get_repository), models: AiModelRepository = Depends(get_ai_models),
              user: User = Depends(current_user)):
    """What the AI has learned so far for this level."""
    load_project(project_id, repo, user.id)
    model = models.get(project_id)
    return {
        "samples_seen": model["samples_seen"],
        "version": model["version"],
        "difficulty": difficulty_of(model),
        "parameters": model["parameters"],
    }


@router.post("/obstacles")
def add_learned_obstacles(
    project_id: int,
    body: ObstacleRequest,
    repo=Depends(get_repository),
    models: AiModelRepository = Depends(get_ai_models),
    user: User = Depends(current_user),
    ai_client: AiServiceClient = Depends(get_ai_client),
):
    """Let the learned model place new obstacles where players struggle least."""
    project = load_project(project_id, repo, user.id)
    model = models.get(project_id)
    started = time.monotonic()
    try:
        reply = ai_client.obstacles(model["parameters"], list(project.scene), body.count)
    except AiServiceError as error:
        raise HTTPException(status_code=502, detail=str(error))
    objects = validate_generated(reply["objects"])
    scene = append_objects(project, objects)
    elapsed = int((time.monotonic() - started) * 1000)
    request_id = models.record_request(project_id, user.id, f"obstacles:{body.count}", "ok", "", elapsed)
    difficulty = float(reply.get("difficulty", difficulty_of(model)))
    models.record_generation(request_id, objects, difficulty)
    result = project_json(repo.update_scene(project_id, user.id, scene))
    result["difficulty"] = difficulty
    result["added"] = len(objects)
    return result
