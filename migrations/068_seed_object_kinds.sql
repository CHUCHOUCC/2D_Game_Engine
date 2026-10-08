insert into object_kinds (code, name, category, solid, movable, collectible, hostile) values
    ('player', 'Jugador', 'player',      true,  true,  false, false),
    ('box',    'Caja',    'obstacle',    true,  true,  false, false),
    ('wall',   'Pared',   'obstacle',    true,  false, false, false),
    ('house',  'Casa',    'building',    true,  false, false, false),
    ('tree',   'Arbol',   'decoration',  true,  false, false, false),
    ('spike',  'Pinchos', 'obstacle',    false, false, false, true),
    ('coin',   'Moneda',  'collectible', false, false, true,  false),
    ('enemy',  'Enemigo', 'enemy',       true,  true,  false, true)
on conflict (code) do nothing;
