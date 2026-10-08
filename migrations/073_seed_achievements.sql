insert into achievements (code, name, description, points) values
    ('first-coin',   'Primera moneda',  'Recoge tu primera moneda',          5),
    ('coin-hoarder', 'Coleccionista',   'Recoge todas las monedas de un nivel', 20),
    ('first-win',    'Primera victoria','Termina un nivel',                  15),
    ('hunter',       'Cazador',         'Derrota 10 enemigos',               20),
    ('untouchable',  'Intocable',       'Gana sin recibir dano',             30)
on conflict (code) do nothing;
