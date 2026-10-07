from psycopg.types.json import Jsonb

from .project import Project

_COLUMNS = "id, owner_id, name, scene, updated_at"


class ProjectRepository:
    """Reads and writes the 'projects' table with hand-written SQL.

    Every query that touches an existing project filters by owner_id, so a
    user can never read or change another user's project: if the project
    does not exist or belongs to someone else, the result is None.
    """

    def __init__(self, connection):
        self._connection = connection

    def create(self, owner_id: int, name: str, scene: list) -> Project:
        row = self._connection.execute(
            f"insert into projects (owner_id, name, scene) values (%s, %s, %s) returning {_COLUMNS}",
            (owner_id, name, Jsonb(scene)),
        ).fetchone()
        return Project(**row)

    def list_by_owner(self, owner_id: int) -> list:
        rows = self._connection.execute(
            f"select {_COLUMNS} from projects where owner_id = %s order by updated_at desc",
            (owner_id,),
        ).fetchall()
        return [Project(**row) for row in rows]

    def find_by_id(self, project_id: int, owner_id: int):
        row = self._connection.execute(
            f"select {_COLUMNS} from projects where id = %s and owner_id = %s",
            (project_id, owner_id),
        ).fetchone()
        return Project(**row) if row else None

    def update_scene(self, project_id: int, owner_id: int, scene: list):
        row = self._connection.execute(
            f"update projects set scene = %s, updated_at = now() "
            f"where id = %s and owner_id = %s returning {_COLUMNS}",
            (Jsonb(scene), project_id, owner_id),
        ).fetchone()
        return Project(**row) if row else None
