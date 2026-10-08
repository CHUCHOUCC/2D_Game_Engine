insert into enemy_types (code, name, health, speed, damage, behavior, texture_code) values
    ('slime',    'Slime',     2, 60,  1, 'chase',  'enemy-slime'),
    ('skeleton', 'Esqueleto', 3, 90,  1, 'patrol', 'enemy-skeleton'),
    ('bat',      'Murcielago',1, 140, 1, 'chase',  'enemy-bat')
on conflict (code) do nothing;
