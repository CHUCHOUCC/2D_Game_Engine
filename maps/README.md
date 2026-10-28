# Ready-made maps

The maps offered when a project is created ("Nuevo proyecto") come from the sample maps that
[Kenney](https://kenney.nl) ships with his asset packs. They are public domain (CC0, see
`kenney/License.txt`): no permission or credit is needed, but we credit Kenney anyway.

| Map | Code | Source |
|---|---|---|
| Mazmorra (Kenney) | `kenney-dungeon` | [Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon) 1.0, `Tiled/sampleMap.tmx` (32 x 20) |
| Reino (Kenney) | `kenney-kingdom` | [1-Bit Pack](https://kenney.nl/assets/1-bit-pack) 1.2, `Tilemap/sample_fantasy.tmx` (48 x 24) |
| Casa (Kenney) | `kenney-house` | [1-Bit Pack](https://kenney.nl/assets/1-bit-pack) 1.2, `Tilemap/sample_interior.tmx` (48 x 24) |

The packs were downloaded from kenney.nl on 2026-10-27. Tiny Dungeon is the same pack the game's
textures already come from.

## How a Tiled map becomes a scene

The engine's world is 50 x 30 tiles of 32 px, and every Kenney tile (16 px, drawn at 2x) becomes
one tile of the world. Each `kenney/*.txt` file is that 50 x 30 grid, one character per tile:

| Char | Kind | Char | Kind | Char | Kind |
|---|---|---|---|---|---|
| `.` | nothing | `#` | `wall` | `T` | `tree` |
| `b` | `bush` | `f` | `fence` | `B` | `box` |
| `R` | `barrel` | `^` | `spike` | `C` | `chest` |
| `v` | `villager` | `k` | `knight` | `z` | `wizard` |
| `e` | `enemy` | `a` | `bat` | `s` | `spider` |
| `O` | `brute` | `P` | `player` | | |

Tiles of the Kenney sheets (index = Tiled gid - 1 for Tiny Dungeon, gid for the 1-Bit Pack):

- **Tiny Dungeon** - walls: 1-8, 13-20, 25-29, 31, 32, 36-40, 43, 44, 57-59; floor, dirt, doors and
  rails: nothing; cabinets, tables, stools and mine carts (54, 55, 63-66, 72-75): `box`; 82
  `barrel`; 89 `chest`; 77 `fence`; 120 `bat`; 122 `spider`; 109 `brute`; 123, 124 `enemy`; people:
  84, 111 `wizard`, 87, 97 `knight`, 86, 98, 100 `villager`.
- **1-Bit Pack, fantasy** - castle, houses, roofs, statues and graves (354-360, 369, 385-387, 401,
  417, 422, 424, 449-451, 488, 491-493, 523-525, 556): `wall`; trees 33, 38, 68: `tree`; 71 and the
  river (137, 138): `bush`; 102, 166: `fence`; 167 `chest`; 227, 241, 297, 452: `box`; 453 `barrel`;
  481 (bones) `spike`; grass, paths, crops, doors and signs: nothing.
- **1-Bit Pack, interior** - 417, 419: `wall`; furniture (228, 229, 236, 237, 239, 257, 258,
  260-262, 265, 269, 273, 305, 337): `box`; 35 `tree`; 59, 154 `villager`; 63 `knight`; 89
  `wizard`; 218 `enemy`; floor, door and candles: nothing.

The samples have no player, so each grid adds a `P` on an open tile; nothing else was changed.
The Kenney samples are scenery: only the dungeon brings enemies to defeat. Add coins or enemies in
the editor (or with the AI) to give the other two a goal.

Rebuild the migration after editing a grid:

```
python tools/build_maps.py     # checks every map and writes migrations/088_seed_kenney_maps.sql
```
