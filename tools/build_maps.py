"""Turns the grids in maps/kenney/ into a migration with the ready-made maps.

    python tools/build_maps.py      # writes the newest map migration (see MIGRATION below)

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
    "w": "water", "_": "bridge", ":": "sand",
    "m": "marksman", "n": "necromancer", "D": "demon", "M": "mimic", "r": "rat",
}
SOLID = {"wall", "tree", "bush", "fence", "water"}
# Things that can stand on a road: when most of their neighbours are road, a
# road tile is put under them too, so people and coins don't sit on a hole of grass.
ON_ROAD = {"villager", "knight", "wizard", "enemy", "bat", "spider", "ghost", "brute", "coin", "potion",
           "chest", "dagger", "hammer", "spear", "staff", "box", "barrel", "player",
           "marksman", "necromancer", "demon", "mimic", "rat"}

# Migrations are history: once applied in production they never change. 088 and
# 089 seeded the first maps; the newest migration (MIGRATION) re-seeds every map
# with "do update", so edit the grids, point MIGRATION at a new number and run this.
MIGRATION = "090_terrain_enemies_and_maps.sql"

MAPS = [
    ("kenney-dungeon", "dungeon.txt", "Mazmorra (Kenney)",
     "Mapa de ejemplo del pack Tiny Dungeon de Kenney (CC0): salas, vías y enemigos"),
    ("kenney-kingdom", "kingdom.txt", "Reino (Kenney)",
     "Castillo con foso, río, aldea y bosque del 1-Bit Pack de Kenney (CC0); un demonio guarda el castillo"),
    ("kenney-house", "house.txt", "Casa (Kenney)",
     "Interior de una casa con sus habitantes, del 1-Bit Pack de Kenney (CC0)"),
    ("kenney-city", "city.txt", "Ciudad (Kenney)",
     "Una ciudad con calles, aceras, edificios, coches, un parque y un lago, del 1-Bit Pack de Kenney (CC0); "
     "recoge las monedas y limpia las calles de monstruos y arqueros"),
    ("kenney-village", "village.txt", "Aldea (Kenney)",
     "Aldea con casas, lago, bosque, campamento y cementerio, del Roguelike/RPG pack de Kenney (CC0); "
     "un demonio acampa al noreste"),
]

# Kinds added with this migration: terrain and the enemies that shoot.
NEW_KINDS_SQL = """-- Terrain ('water' blocks walking; 'sand' and 'bridge' are ground with no body)
-- and new enemies: two that shoot from afar, a boss, a mimic and rats.
insert into object_kinds (code, name, category, solid, movable, collectible, hostile) values
    ('water',       'Agua',           'obstacle',   true,  false, false, false),
    ('sand',        'Arena',          'decoration', false, false, false, false),
    ('bridge',      'Puente',         'decoration', false, false, false, false),
    ('marksman',    'Arquero oscuro', 'enemy',      true,  true,  false, true),
    ('necromancer', 'Nigromante',     'enemy',      true,  true,  false, true),
    ('demon',       'Demonio',        'enemy',      true,  true,  false, true),
    ('mimic',       'Mímico',         'enemy',      true,  true,  false, true),
    ('rat',         'Rata',           'enemy',      true,  true,  false, true)
on conflict (code) do nothing;

insert into object_physics (kind, body_type, material_id, mass, drag, immovable)
select k.kind, k.body_type, m.id, k.mass, k.drag, k.immovable
from (values
    ('water',       'static',  'stone', 1.0,  0,   true),
    ('sand',        'none',    'stone', 1.0,  0,   true),
    ('bridge',      'none',    'wood',  1.0,  0,   true),
    ('marksman',    'dynamic', 'flesh', 1.5,  200, false),
    ('necromancer', 'dynamic', 'flesh', 1.5,  200, false),
    ('demon',       'dynamic', 'flesh', 12.0, 300, false),
    ('mimic',       'dynamic', 'wood',  1.5,  200, false),
    ('rat',         'dynamic', 'flesh', 0.5,  100, false)
) as k (kind, body_type, material, mass, drag, immovable)
join physics_materials m on m.code = k.material
on conflict (kind) do nothing;

insert into textures (pack_id, code, kind, file_path, width, height, frames)
select p.id, t.code, t.kind, 'textures/' || t.code || '.png', t.size, t.size, 1
from texture_packs p
cross join (values
    ('water', 'water', 32), ('sand', 'sand', 32), ('bridge', 'bridge', 32), ('marksman', 'marksman', 32),
    ('necromancer', 'necromancer', 32), ('demon', 'demon', 32), ('mimic', 'mimic', 32), ('rat', 'rat', 32)
) as t (code, kind, size)
where p.code = 'kenney-tiny'
on conflict (pack_id, code) do nothing;

insert into enemy_types (code, name, health, speed, damage, behavior, texture_code) values
    ('marksman',    'Arquero oscuro', 3,  75,  1, 'patrol', 'marksman'),
    ('necromancer', 'Nigromante',     4,  55,  1, 'patrol', 'necromancer'),
    ('demon',       'Demonio',        30, 55,  2, 'chase',  'demon'),
    ('mimic',       'Mímico',         5,  140, 2, 'idle',   'mimic'),
    ('rat',         'Rata',           1,  150, 1, 'chase',  'rat')
on conflict (code) do nothing;

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
    values = []
    for code, grid_name, name, description in MAPS:
        rows = read_grid(ROOT / "maps" / "kenney" / grid_name)
        check(code, rows)
        scene = scene_of(rows)
        assert len(scene) <= MAX_OBJECTS, f"{code}: {len(scene)} objects, at most {MAX_OBJECTS}"
        print(f"{code:15} {len(scene):4} objects")
        values.append(f"    ({sql_text(code)}, {sql_text(name)}, {sql_text(description)},\n"
                      f"     {sql_text(json.dumps(scene, separators=(',', ':')))}::jsonb)")
    sql = ("-- Ready-made maps: Kenney's sample maps (CC0), see maps/README.md.\n"
           "-- Generated by tools/build_maps.py from maps/kenney/*.txt; do not edit by hand.\n"
           + NEW_KINDS_SQL
           + "insert into level_templates (code, name, description, scene) values\n"
           + ",\n".join(values)
           + "\non conflict (code) do update\n"
           + "    set name = excluded.name, description = excluded.description, scene = excluded.scene;\n")
    out = ROOT / "migrations" / MIGRATION
    out.write_text(sql, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
