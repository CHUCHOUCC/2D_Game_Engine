create table if not exists scene_layers (
    id       bigint generated always as identity primary key,
    scene_id bigint   not null references scenes (id) on delete cascade,
    name     text     not null,
    z_index  smallint not null default 0,
    visible  boolean  not null default true,
    locked   boolean  not null default false,
    unique (scene_id, name)
);
