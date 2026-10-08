-- Editor preferences chosen in the settings wheel.
create table if not exists user_settings (
    user_id      bigint      primary key references users (id) on delete cascade,
    theme        text        not null default 'dark' check (theme in ('light', 'dark', 'system')),
    language     text        not null default 'es' check (language in ('es', 'en')),
    show_grid    boolean     not null default true,
    snap_to_grid boolean     not null default true,
    grid_size    smallint    not null default 32 check (grid_size between 8 and 128),
    music_volume smallint    not null default 70 check (music_volume between 0 and 100),
    sfx_volume   smallint    not null default 80 check (sfx_volume between 0 and 100),
    updated_at   timestamptz not null default now()
);
