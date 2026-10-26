-- More enemies, weapons, potions, chests and obstacles.
insert into object_kinds (code, name, category, solid, movable, collectible, hostile) values
    ('bat',    'Murciélago', 'enemy',       false, true,  false, true),
    ('spider', 'Araña',      'enemy',       true,  true,  false, true),
    ('ghost',  'Fantasma',   'enemy',       false, true,  false, true),
    ('brute',  'Ogro',       'enemy',       true,  true,  false, true),
    ('chest',  'Cofre',      'obstacle',    true,  false, false, false),
    ('potion', 'Poción',     'collectible', false, false, true,  false),
    ('sword',  'Espada',     'collectible', false, false, true,  false),
    ('axe',    'Hacha',      'collectible', false, false, true,  false),
    ('wand',   'Varita',     'collectible', false, false, true,  false),
    ('bow',    'Arco',       'collectible', false, false, true,  false),
    ('barrel', 'Barril',     'obstacle',    true,  true,  false, false),
    ('fence',  'Valla',      'obstacle',    true,  false, false, false),
    ('bush',   'Arbusto',    'decoration',  true,  false, false, false)
on conflict (code) do nothing;

insert into object_physics (kind, body_type, material_id, mass, drag, immovable)
select k.kind, k.body_type, m.id, k.mass, k.drag, k.immovable
from (values
    ('bat',    'dynamic', 'flesh', 0.5, 100, false),
    ('spider', 'dynamic', 'flesh', 1.0, 200, false),
    ('ghost',  'dynamic', 'flesh', 1.0, 100, false),
    ('brute',  'dynamic', 'flesh', 4.0, 300, false),
    ('chest',  'static',  'wood',  1.0, 0,   true),
    ('potion', 'static',  'metal', 1.0, 0,   true),
    ('sword',  'static',  'metal', 1.0, 0,   true),
    ('axe',    'static',  'metal', 1.0, 0,   true),
    ('wand',   'static',  'wood',  1.0, 0,   true),
    ('bow',    'static',  'wood',  1.0, 0,   true),
    ('barrel', 'dynamic', 'wood',  3.0, 500, false),
    ('fence',  'static',  'wood',  1.0, 0,   true),
    ('bush',   'static',  'wood',  1.0, 0,   true)
) as k (kind, body_type, material, mass, drag, immovable)
join physics_materials m on m.code = k.material
on conflict (kind) do nothing;

insert into enemy_types (code, name, health, speed, damage, behavior, texture_code) values
    ('spider', 'Araña',    2, 130, 1, 'chase', 'spider'),
    ('ghost',  'Fantasma', 3, 60,  1, 'chase', 'ghost'),
    ('brute',  'Ogro',     8, 50,  2, 'chase', 'brute')
on conflict (code) do nothing;
