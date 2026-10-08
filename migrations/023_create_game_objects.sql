-- Normalised copy of a scene objects (projects.scene stays the fast path).
create table if not exists game_objects (
    id         bigint generated always as identity primary key,
    scene_id   bigint not null references scenes (id) on delete cascade,
    layer_id   bigint references scene_layers (id) on delete set null,
    object_uid text   not null,
    kind       text   not null references object_kinds (code),
    x          real   not null,
    y          real   not null,
    width      real   not null default 32,
    height     real   not null default 32,
    rotation   real   not null default 0,
    properties jsonb  not null default '{}'::jsonb,
    unique (scene_id, object_uid)
);
