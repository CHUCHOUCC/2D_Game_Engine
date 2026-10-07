import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ValidationError

from app.ai_client import AiServiceClient, AiServiceError
from app.database import get_connection
from .repository import ProjectRepository

router = APIRouter(prefix="/projects", tags=["projects"])


class GameObjectIn(BaseModel):
    id: str
    kind: str
    x: float
    y: float


class ProjectCreate(BaseModel):
    name: str


class SceneUpdate(BaseModel):
    scene: List[GameObjectIn]


class AiRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)


def get_repository():
    """Provide a repository bound to one connection per request.

    The transaction is committed when the request succeeds and rolled back
    if it raises.
    """
    with get_connection() as connection:
        yield ProjectRepository(connection)


def get_ai_client() -> AiServiceClient:
    url = os.environ.get("AI_SERVICE_URL")
    key = os.environ.get("AI_SERVICE_KEY")
    if not url or not key:
        raise HTTPException(status_code=503, detail="AI service is not configured")
    return AiServiceClient(url, key)


def current_owner_id() -> int:
    # TEMPORARY: always the demo user (id 1) until AuthService reads the
    # token and returns the real user.
    return 1


def _to_json(project):
    return {
        "id": project.id,
        "owner_id": project.owner_id,
        "name": project.name,
        "scene": project.scene,
        "updated_at": project.updated_at.isoformat(),
    }


@router.post("", status_code=201)
def create_project(body: ProjectCreate, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    return _to_json(repo.create(owner_id, body.name, []))


@router.get("")
def list_projects(repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    return [_to_json(p) for p in repo.list_by_owner(owner_id)]


@router.get("/{project_id}")
def get_project(project_id: int, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    project = repo.find_by_id(project_id, owner_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_json(project)


@router.put("/{project_id}/scene")
def save_scene(project_id: int, body: SceneUpdate, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    scene = [obj.model_dump() for obj in body.scene]
    project = repo.update_scene(project_id, owner_id, scene)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_json(project)


def _with_unique_ids(existing: list, new: list) -> list:
    """Give each new object an id that is not used yet in the scene."""
    used = {obj["id"] for obj in existing}
    result = []
    for obj in new:
        candidate, n = obj["id"], 1
        while candidate in used:
            n += 1
            candidate = f"{obj['id']}-{n}"
        used.add(candidate)
        result.append({**obj, "id": candidate})
    return result


@router.post("/{project_id}/ai")
def add_objects_with_ai(
    project_id: int,
    body: AiRequest,
    repo=Depends(get_repository),
    owner_id: int = Depends(current_owner_id),
    ai_client: AiServiceClient = Depends(get_ai_client),
):
    """Ask the AI service for new objects and add them to the project's scene.

    The backend validates the AI service's answer again before saving it.
    """
    project = repo.find_by_id(project_id, owner_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        generated = ai_client.generate(body.prompt)
        validated = [GameObjectIn(**obj).model_dump() for obj in generated]
    except AiServiceError as error:
        raise HTTPException(status_code=502, detail=str(error))
    except (ValidationError, TypeError):
        raise HTTPException(status_code=502, detail="AI service returned invalid objects")
    scene = list(project.scene) + _with_unique_ids(project.scene, validated)
    return _to_json(repo.update_scene(project_id, owner_id, scene))
