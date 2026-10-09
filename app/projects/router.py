import os

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import ValidationError

from app.ai_client import AiServiceClient, AiServiceError
from app.auth.dependencies import current_user
from app.auth.user import User
from app.database import database_connection
from .repository import ProjectRepository
from .schemas import AiRequest, GameObjectIn, ProjectCreate, ProjectRename, SceneUpdate
from .world import MAX_OBJECTS

router = APIRouter(prefix="/projects", tags=["projects"])


def get_repository(connection=Depends(database_connection)):
    """Provide a project repository bound to the request's shared connection."""
    return ProjectRepository(connection)


def get_ai_client() -> AiServiceClient:
    url = os.environ.get("AI_SERVICE_URL")
    key = os.environ.get("AI_SERVICE_KEY")
    if not url or not key:
        raise HTTPException(status_code=503, detail="AI service is not configured")
    return AiServiceClient(url, key)


def current_owner_id(user: User = Depends(current_user)) -> int:
    """The id of the logged-in user: every project query is filtered by it."""
    return user.id


def project_json(project):
    return {
        "id": project.id,
        "owner_id": project.owner_id,
        "name": project.name,
        "scene": project.scene,
        "updated_at": project.updated_at.isoformat(),
    }


def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Project not found")


def load_project(project_id: int, repo, owner_id: int):
    project = repo.find_by_id(project_id, owner_id)
    if project is None:
        raise _not_found()
    return project


@router.get("/templates")
def list_templates(repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    """Starter scenes a new project can be created from."""
    return [dict(row) for row in repo.list_templates()]


@router.post("", status_code=201)
def create_project(body: ProjectCreate, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    scene = []
    if body.template:
        scene = repo.template_scene(body.template)
        if scene is None:
            raise HTTPException(status_code=422, detail="Unknown template")
    return project_json(repo.create(owner_id, body.name, scene))


@router.get("")
def list_projects(repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    return [project_json(p) for p in repo.list_by_owner(owner_id)]


@router.get("/{project_id}")
def get_project(project_id: int, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    return project_json(load_project(project_id, repo, owner_id))


@router.patch("/{project_id}")
def rename_project(project_id: int, body: ProjectRename, repo=Depends(get_repository),
                   owner_id: int = Depends(current_owner_id)):
    project = repo.rename(project_id, owner_id, body.name)
    if project is None:
        raise _not_found()
    return project_json(project)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    if not repo.delete(project_id, owner_id):
        raise _not_found()
    return Response(status_code=204)


@router.post("/{project_id}/duplicate", status_code=201)
def duplicate_project(project_id: int, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    """Clone a project: same scene, name with ' (copia)' appended."""
    original = load_project(project_id, repo, owner_id)
    name = f"{original.name} (copia)"[:100]
    return project_json(repo.create(owner_id, name, list(original.scene)))


@router.put("/{project_id}/scene")
def save_scene(project_id: int, body: SceneUpdate, repo=Depends(get_repository),
               owner_id: int = Depends(current_owner_id)):
    scene = [obj.model_dump() for obj in body.scene]
    project = repo.update_scene(project_id, owner_id, scene)
    if project is None:
        raise _not_found()
    repo.save_version(project_id, owner_id, scene, body.note)
    return project_json(project)


@router.get("/{project_id}/versions")
def list_versions(project_id: int, repo=Depends(get_repository), owner_id: int = Depends(current_owner_id)):
    load_project(project_id, repo, owner_id)
    return [
        {**row, "created_at": row["created_at"].isoformat()}
        for row in (dict(r) for r in repo.list_versions(project_id))
    ]


@router.post("/{project_id}/versions/{version_number}/restore")
def restore_version(project_id: int, version_number: int, repo=Depends(get_repository),
                    owner_id: int = Depends(current_owner_id)):
    load_project(project_id, repo, owner_id)
    scene = repo.find_version(project_id, version_number)
    if scene is None:
        raise HTTPException(status_code=404, detail="Version not found")
    project = repo.update_scene(project_id, owner_id, scene)
    repo.save_version(project_id, owner_id, scene, f"Restaurada la version {version_number}")
    return project_json(project)


def with_unique_ids(existing: list, new: list) -> list:
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


def validate_generated(objects: list) -> list:
    """Check again whatever the AI service returned; it is never trusted blindly.

    The AI may not add a second player: extra 'player' objects are dropped.
    """
    try:
        validated = [GameObjectIn(**obj).model_dump() for obj in objects]
    except (ValidationError, TypeError):
        raise HTTPException(status_code=502, detail="AI service returned invalid objects")
    return [obj for obj in validated if obj["kind"] != "player"]


def append_objects(project, new_objects: list) -> list:
    scene = list(project.scene) + with_unique_ids(project.scene, new_objects)
    if len(scene) > MAX_OBJECTS:
        raise HTTPException(status_code=422, detail=f"A scene can have at most {MAX_OBJECTS} objects")
    return scene


@router.post("/{project_id}/ai")
def add_objects_with_ai(
    project_id: int,
    body: AiRequest,
    repo=Depends(get_repository),
    owner_id: int = Depends(current_owner_id),
    ai_client: AiServiceClient = Depends(get_ai_client),
):
    """Ask the AI service for new objects and add them to the project's scene."""
    project = load_project(project_id, repo, owner_id)
    try:
        generated = ai_client.generate(body.prompt, list(project.scene))
    except AiServiceError as error:
        raise HTTPException(status_code=502, detail=str(error))
    scene = append_objects(project, validate_generated(generated))
    return project_json(repo.update_scene(project_id, owner_id, scene))
