insert into object_physics (kind, body_type, material_id, mass, drag, immovable)
select k.kind, k.body_type, m.id, k.mass, k.drag, k.immovable
from (values
    ('player', 'dynamic', 'flesh', 1.0, 600, false),
    ('box',    'dynamic', 'wood',  2.0, 400, false),
    ('wall',   'static',  'stone', 1.0, 0,   true),
    ('house',  'static',  'wood',  1.0, 0,   true),
    ('tree',   'static',  'wood',  1.0, 0,   true),
    ('spike',  'static',  'metal', 1.0, 0,   true),
    ('coin',   'static',  'metal', 1.0, 0,   true),
    ('enemy',  'dynamic', 'flesh', 1.5, 200, false)
) as k (kind, body_type, material, mass, drag, immovable)
join physics_materials m on m.code = k.material
on conflict (kind) do nothing;
