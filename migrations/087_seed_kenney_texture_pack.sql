-- The textures now come from Kenney's Tiny Dungeon and Tiny Town packs (CC0).
insert into texture_packs (code, name, author, license) values
    ('kenney-tiny', 'Kenney Tiny Dungeon + Tiny Town', 'Kenney (www.kenney.nl)', 'CC0')
on conflict (code) do nothing;

insert into textures (pack_id, code, kind, file_path, width, height, frames)
select p.id, t.code, t.kind, 'textures/' || t.code || '.png', t.size, t.size, 1
from texture_packs p
cross join (values
    ('player', 'player', 32), ('villager', 'villager', 32), ('knight', 'knight', 32), ('wizard', 'wizard', 32),
    ('enemy-slime', 'enemy', 32), ('bat', 'bat', 32), ('spider', 'spider', 32), ('ghost', 'ghost', 32),
    ('brute', 'brute', 32), ('wall', 'wall', 32), ('box', 'box', 32), ('barrel', 'barrel', 32),
    ('tree', 'tree', 32), ('bush', 'bush', 32), ('fence', 'fence', 32), ('coin', 'coin', 32),
    ('chest', 'chest', 32), ('potion', 'potion', 32), ('sword', 'sword', 32), ('axe', 'axe', 32),
    ('wand', 'wand', 32), ('bow', 'bow', 32), ('house', 'house', 96)
) as t (code, kind, size)
where p.code = 'kenney-tiny'
on conflict (pack_id, code) do nothing;
