-- Snapshot of a scene every time it is saved, to go back to an older version.
create table if not exists project_versions (
    id             bigint generated always as identity primary key,
    project_id     bigint      not null references projects (id) on delete cascade,
    version_number integer     not null,
    scene          jsonb       not null,
    note           text        not null default '',
    created_by     bigint      references users (id) on delete set null,
    created_at     timestamptz not null default now(),
    unique (project_id, version_number)
);
