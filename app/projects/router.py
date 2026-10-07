from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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


def get_repository():
    """Provide a repository bound to one connection per request.

    The transaction is committed when the request succeeds and rolled back
    if it raises.
    """
    with get_connection() as connection:
        yield ProjectRepository(connection)


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
