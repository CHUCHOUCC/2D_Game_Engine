-- A game project: its owner and the scene as a JSON array of game objects.
create table if not exists projects (
    id         bigint generated always as identity primary key,
    owner_id   bigint      not null references users (id) on delete cascade,
    name       text        not null check (length(name) between 1 and 100),
    scene      jsonb       not null default '[]'::jsonb,
    updated_at timestamptz not null default now()
);
