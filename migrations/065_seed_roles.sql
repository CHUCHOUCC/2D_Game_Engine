insert into roles (name, description) values
    ('player',  'Can play published levels'),
    ('creator', 'Can create and edit their own projects'),
    ('admin',   'Can manage every user and project')
on conflict (name) do nothing;
