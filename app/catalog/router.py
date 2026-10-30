from fastapi import APIRouter, Depends, Request

from app.cache import PUBLIC, cached_json, reference_cache
from app.database import lazy_database_connection

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

    def character_lines(self) -> list:
        return self._connection.execute(
            "select kind, line from character_lines order by kind, id"
        ).fetchall()

    def textures(self) -> list:
        return self._connection.execute(
            "select t.code, t.kind, t.file_path, t.width, t.height, t.frames, p.code as pack "
            "from textures t join texture_packs p on p.id = t.pack_id order by t.id"
        ).fetchall()


def get_catalog(connection=Depends(lazy_database_connection)) -> CatalogRepository:
    # Lazy: when the answer comes from the cache, no connection is opened at all.
    return CatalogRepository(connection)


# The catalog only changes with a migration: it is cached in memory (reference_cache) and the
# browser may keep it too (ETag + public Cache-Control).

@router.get("/kinds")
def list_kinds(request: Request, catalog: CatalogRepository = Depends(get_catalog)):
    data = reference_cache.get_or_load("catalog:kinds", lambda: [dict(row) for row in catalog.kinds()])
    return cached_json(request, data, PUBLIC)


@router.get("/enemies")
def list_enemies(request: Request, catalog: CatalogRepository = Depends(get_catalog)):
    data = reference_cache.get_or_load("catalog:enemies", lambda: [dict(row) for row in catalog.enemies()])
    return cached_json(request, data, PUBLIC)


def _group_lines(rows) -> dict:
    lines: dict = {}
    for row in rows:
        lines.setdefault(row["kind"], []).append(row["line"])
    return lines


@router.get("/characters")
def list_character_lines(request: Request, catalog: CatalogRepository = Depends(get_catalog)):
    """What each 2D character can say, grouped by kind."""
    data = reference_cache.get_or_load("catalog:characters", lambda: _group_lines(catalog.character_lines()))
    return cached_json(request, data, PUBLIC)


@router.get("/textures")
def list_textures(request: Request, catalog: CatalogRepository = Depends(get_catalog)):
    data = reference_cache.get_or_load("catalog:textures", lambda: [dict(row) for row in catalog.textures()])
    return cached_json(request, data, PUBLIC)
