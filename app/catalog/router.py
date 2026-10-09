from fastapi import APIRouter, Depends

from app.database import database_connection

router = APIRouter(prefix="/catalog", tags=["catalog"])


class CatalogRepository:
    """Read-only reference data: object kinds with their physics, enemy types, textures."""

    def __init__(self, connection):
        self._connection = connection

    def kinds(self) -> list:
        return self._connection.execute(
            "select k.code, k.name, k.category, k.solid, k.movable, k.collectible, k.hostile, "
            "coalesce(p.body_type, 'none') as body_type, coalesce(p.mass, 1) as mass, "
            "coalesce(p.drag, 0) as drag, coalesce(m.bounce, 0) as bounce "
            "from object_kinds k left join object_physics p on p.kind = k.code "
            "left join physics_materials m on m.id = p.material_id order by k.code"
        ).fetchall()

    def enemies(self) -> list:
        return self._connection.execute(
            "select code, name, health, speed, damage, behavior, texture_code from enemy_types order by id"
        ).fetchall()

    def textures(self) -> list:
        return self._connection.execute(
            "select t.code, t.kind, t.file_path, t.width, t.height, t.frames, p.code as pack "
            "from textures t join texture_packs p on p.id = t.pack_id order by t.id"
        ).fetchall()


def get_catalog(connection=Depends(database_connection)) -> CatalogRepository:
    return CatalogRepository(connection)


@router.get("/kinds")
def list_kinds(catalog: CatalogRepository = Depends(get_catalog)):
    return [dict(row) for row in catalog.kinds()]


@router.get("/enemies")
def list_enemies(catalog: CatalogRepository = Depends(get_catalog)):
    return [dict(row) for row in catalog.enemies()]


@router.get("/textures")
def list_textures(catalog: CatalogRepository = Depends(get_catalog)):
    return [dict(row) for row in catalog.textures()]
