-- Reusable objects a user saves from the inspector.
create table if not exists prefabs (
    id         bigint generated always as identity primary key,
    owner_id   bigint      not null references users (id) on delete cascade,
    name       text        not null,
    kind       text        not null references object_kinds (code),
    properties jsonb       not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);
