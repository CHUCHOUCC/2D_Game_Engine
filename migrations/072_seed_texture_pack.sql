insert into texture_packs (code, name, author, license) values
    ('pixel-village', 'Pixel Village', '2D Engine team', 'CC0')
on conflict (code) do nothing;

insert into textures (pack_id, code, kind, file_path, width, height, frames)
select p.id, t.code, t.kind, t.file_path, 32, 32, t.frames
from texture_packs p
cross join (values
    ('player',         'player', 'textures/player.png',         4),
    ('box',            'box',    'textures/box.png',            1),
    ('wall',           'wall',   'textures/wall.png',           1),
    ('house',          'house',  'textures/house.png',          1),
    ('tree',           'tree',   'textures/tree.png',           1),
    ('spike',          'spike',  'textures/spike.png',          1),
    ('coin',           'coin',   'textures/coin.png',           4),
    ('enemy-slime',    'enemy',  'textures/enemy-slime.png',    2),
    ('grass',          null,     'textures/grass.png',          1)
) as t (code, kind, file_path, frames)
where p.code = 'pixel-village'
on conflict (pack_id, code) do nothing;
