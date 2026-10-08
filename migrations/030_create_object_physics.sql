-- Physics body of each object kind.
create table if not exists object_physics (
    kind        text     primary key references object_kinds (code) on delete cascade,
    body_type   text     not null check (body_type in ('static', 'dynamic', 'kinematic', 'none')),
    material_id smallint references physics_materials (id),
    mass        real     not null default 1 check (mass > 0),
    drag        real     not null default 0 check (drag >= 0),
    immovable   boolean  not null default false
);
