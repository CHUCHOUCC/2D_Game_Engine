-- Surface behaviour used by Arcade Physics bodies.
create table if not exists physics_materials (
    id       smallint generated always as identity primary key,
    code     text not null unique,
    friction real not null default 0.5 check (friction between 0 and 1),
    bounce   real not null default 0 check (bounce between 0 and 1),
    density  real not null default 1 check (density > 0)
);
