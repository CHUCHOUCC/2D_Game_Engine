"""Turns the grids in maps/kenney/ into a migration with the ready-made maps.

    python tools/build_maps.py      # writes migrations/088_seed_kenney_maps.sql and 089_seed_city_maps.sql

Each grid is 50 x 30 characters, one per tile of the world (see maps/README.md).
Before writing, every map is checked: exactly one player, no unknown characters,
and every chest reachable on foot from the player.
"""
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_OBJECTS = 1500  # same as app/projects/world.py
COLUMNS, ROWS, TILE = 50, 30, 32
KINDS = {
    "#": "wall", "T": "tree", "b": "bush", "f": "fence", "B": "box", "R": "barrel", "^": "spike",
    "C": "chest", "v": "villager", "k": "knight", "z": "wizard", "e": "enemy", "a": "bat",
    "s": "spider", "O": "brute", "P": "player", "g": "ghost", "c": "coin", "p": "potion",
    "d": "dagger", "h": "hammer", "l": "spear", "t": "staff", "=": "path",
}
SOLID = {"wall", "tree", "bush", "fence"}
# Things that can stand on a road: when most of their neighbours are road, a
# road tile is put under them too, so people and coins don't sit on a hole of grass.
ON_ROAD = {"villager", "knight", "wizard", "enemy", "bat", "spider", "ghost", "brute", "coin", "potion",
           "chest", "dagger", "hammer", "spear", "staff", "box", "barrel", "player"}

# Each migration and the maps it seeds. 088 is already applied in production,
# so new maps go in a new migration instead of changing it.
MIGRATIONS = {
    "088_seed_kenney_maps.sql": [
        ("kenney-dungeon", "dungeon.txt", "Mazmorra (Kenney)",
         "Mapa de ejemplo del pack Tiny Dungeon de Kenney (CC0): salas, vías y enemigos"),
        ("kenney-kingdom", "kingdom.txt", "Reino (Kenney)",
         "Castillo, aldea, río y bosque del 1-Bit Pack de Kenney (CC0); agrega monedas o enemigos"),
        ("kenney-house", "house.txt", "Casa (Kenney)",
         "Interior de una casa con sus habitantes, del 1-Bit Pack de Kenney (CC0)"),
    ],
    "089_seed_city_maps.sql": [
        ("kenney-city", "city.txt", "Ciudad (Kenney)",
         "Una ciudad con calles, aceras, edificios, coches y un parque, del 1-Bit Pack de Kenney (CC0); "
         "recoge las monedas y limpia las calles de monstruos"),
        ("kenney-village", "village.txt", "Aldea (Kenney)",
         "Aldea con casas, lago, bosque, campamento y cementerio, del Roguelike/RPG pack de Kenney (CC0)"),
    ],
}
MAPS = [entry for maps in MIGRATIONS.values() for entry in maps]

# Kinds added together with the city maps (089): the road tile and four weapons.
NEW_KINDS_SQL = """-- New kinds: 'path' (road or stone drawn under everything, no body) and the
-- weapons of the newer heroes, which can also be placed as pickups.
insert into object_kinds (code, name, category, solid, movable, collectible, hostile) values
    ('path',   'Camino',  'decoration',  false, false, false, false),
    ('dagger', 'Dagas',   'collectible', false, false, true,  false),
    ('hammer', 'Martillo','collectible', false, false, true,  false),
    ('spear',  'Lanza',   'collectible', false, false, true,  false),
    ('staff',  'Báculo',  'collectible', false, false, true,  false)
on conflict (code) do nothing;

insert into object_physics (kind, body_type, material_id, mass, drag, immovable)
select k.kind, k.body_type, m.id, k.mass, k.drag, k.immovable
from (values
    ('path',   'none',   'stone', 1.0, 0, true),
    ('dagger', 'static', 'metal', 1.0, 0, true),
    ('hammer', 'static', 'metal', 1.0, 0, true),
    ('spear',  'static', 'metal', 1.0, 0, true),
    ('staff',  'static', 'wood',  1.0, 0, true)
) as k (kind, body_type, material, mass, drag, immovable)
join physics_materials m on m.code = k.material
on conflict (kind) do nothing;

insert into textures (pack_id, code, kind, file_path, width, height, frames)
select p.id, t.code, t.kind, 'textures/' || t.code || '.png', 32, 32, 1
from texture_packs p
cross join (values
    ('path', 'path'), ('dagger', 'dagger'), ('hammer', 'hammer'), ('spear', 'spear'), ('staff', 'staff')
) as t (code, kind)
where p.code = 'kenney-tiny'
on conflict (pack_id, code) do nothing;

"""


def read_grid(path: Path) -> list:
    rows = [line.rstrip("\n") for line in path.read_text(encoding="utf-8").splitlines() if not line.startswith("#")]
    assert len(rows) == ROWS, f"{path.name}: {len(rows)} rows, expected {ROWS}"
    for n, row in enumerate(rows):
        assert len(row) == COLUMNS, f"{path.name}: row {n} has {len(row)} columns"
        unknown = set(row) - set(KINDS) - {"."}
        assert not unknown, f"{path.name}: unknown characters {unknown}"
    return rows


def on_road(rows: list, col: int, row: int) -> bool:
    around = ((col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1))
    roads = sum(1 for c, r in around if 0 <= c < COLUMNS and 0 <= r < ROWS and rows[r][c] == "=")
    return roads >= 2


def scene_of(rows: list) -> list:
    objects, counts = [], {}

    def add(kind: str, col: int, row: int) -> None:
        counts[kind] = counts.get(kind, 0) + 1
        objects.append({"id": f"{kind}-{counts[kind]}", "kind": kind,
                        "x": col * TILE + TILE // 2, "y": row * TILE + TILE // 2})

    for row, line in enumerate(rows):
        for col, char in enumerate(line):
            if char == ".":
                continue
            kind = KINDS[char]
            if kind in ON_ROAD and on_road(rows, col, row):
                add("path", col, row)
            add(kind, col, row)
    return objects


def check(code: str, rows: list) -> None:
    starts = [(c, r) for r, line in enumerate(rows) for c, ch in enumerate(line) if ch == "P"]
    assert len(starts) == 1, f"{code}: needs exactly one player"
    seen, queue = {starts[0]}, deque(starts)
    while queue:
        col, row = queue.popleft()
        for c, r in ((col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)):
            if 0 <= c < COLUMNS and 0 <= r < ROWS and (c, r) not in seen and KINDS.get(rows[r][c]) not in SOLID:
                seen.add((c, r))
                queue.append((c, r))
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch == "C":
                assert (c, r) in seen, f"{code}: the chest at ({c}, {r}) cannot be reached"


def sql_text(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    for file_name, maps in MIGRATIONS.items():
        values = []
        for code, grid_name, name, description in maps:
            rows = read_grid(ROOT / "maps" / "kenney" / grid_name)
            check(code, rows)
            scene = scene_of(rows)
            assert len(scene) <= MAX_OBJECTS, f"{code}: {len(scene)} objects, at most {MAX_OBJECTS}"
            print(f"{code:15} {len(scene):4} objects")
            values.append(f"    ({sql_text(code)}, {sql_text(name)}, {sql_text(description)},\n"
                          f"     {sql_text(json.dumps(scene, separators=(',', ':')))}::jsonb)")
        sql = ("-- Ready-made maps: Kenney's sample maps (CC0), see maps/README.md.\n"
               "-- Generated by tools/build_maps.py from maps/kenney/*.txt; do not edit by hand.\n"
               + (NEW_KINDS_SQL if file_name.startswith("089") else "")
               + "insert into level_templates (code, name, description, scene) values\n"
               + ",\n".join(values) + "\non conflict (code) do nothing;\n")
        out = ROOT / "migrations" / file_name
        out.write_text(sql, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
