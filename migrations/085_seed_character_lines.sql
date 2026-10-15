insert into character_lines (kind, line) values
    ('villager', '¡Hola, viajero! Cuidado con los slimes.'),
    ('villager', 'Dicen que hay monedas detrás de las casas.'),
    ('villager', 'Las cajas se pueden empujar, ¿lo sabías?'),
    ('knight',   'Ataca con Espacio: tres golpes y el enemigo cae.'),
    ('knight',   'Ningún pincho me detendrá.'),
    ('knight',   'Protejo esta aldea desde hace años.'),
    ('wizard',   'La IA aprende de cada partida que juegas...'),
    ('wizard',   'Cuanto mejor juegas, más difícil se vuelve.'),
    ('wizard',   'Recoge todas las monedas para ganar.')
on conflict (kind, line) do nothing;
