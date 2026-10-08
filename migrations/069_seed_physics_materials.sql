insert into physics_materials (code, friction, bounce, density) values
    ('stone', 0.9, 0.0, 2.5),
    ('wood',  0.6, 0.1, 0.7),
    ('flesh', 0.5, 0.2, 1.0),
    ('metal', 0.3, 0.3, 7.8)
on conflict (code) do nothing;
