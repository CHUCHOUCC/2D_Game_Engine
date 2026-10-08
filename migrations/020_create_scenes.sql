-- World settings of a project scene (size, background, physics).
create table if not exists scenes (
    id               bigint generated always as identity primary key,
    project_id       bigint      not null references projects (id) on delete cascade,
    name             text        not null default 'Main',
    width            integer     not null default 1600 check (width between 320 and 8192),
    height           integer     not null default 960 check (height between 240 and 8192),
    tile_size        smallint    not null default 32,
    background_color text        not null default '#2d5a27',
    gravity_x        real        not null default 0,
    gravity_y        real        not null default 0,
    created_at       timestamptz not null default now()
);
