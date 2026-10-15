insert into object_kinds (code, name, category, solid, movable, collectible, hostile) values
    ('villager', 'Aldeano',   'character', true, true, false, false),
    ('knight',   'Caballero', 'character', true, true, false, false),
    ('wizard',   'Mago',      'character', true, true, false, false)
on conflict (code) do nothing;

insert into object_physics (kind, body_type, material_id, mass, drag, immovable)
select k.code, 'dynamic', m.id, 1.2, 300, false
from object_kinds k join physics_materials m on m.code = 'flesh'
where k.category = 'character'
on conflict (kind) do nothing;

insert into textures (pack_id, code, kind, file_path, width, height, frames)
select p.id, t.code, t.code, 'textures/' || t.code || '.png', 32, 32, 4
from texture_packs p
cross join (values ('villager'), ('knight'), ('wizard')) as t (code)
where p.code = 'pixel-village'
on conflict (pack_id, code) do nothing;
