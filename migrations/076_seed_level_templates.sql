insert into level_templates (code, name, description, scene) values
    ('empty', 'Vacio', 'Una escena sin objetos', '[]'::jsonb),
    ('village', 'Aldea', 'Casas, paredes y algunas monedas',
     '[{"id":"house-1","kind":"house","x":320,"y":256},
       {"id":"house-2","kind":"house","x":640,"y":256},
       {"id":"wall-1","kind":"wall","x":480,"y":448},
       {"id":"coin-1","kind":"coin","x":480,"y":320},
       {"id":"coin-2","kind":"coin","x":800,"y":512},
       {"id":"enemy-1","kind":"enemy","x":960,"y":384}]'::jsonb)
on conflict (code) do nothing;
