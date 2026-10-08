create table if not exists project_members (
    project_id bigint      not null references projects (id) on delete cascade,
    user_id    bigint      not null references users (id) on delete cascade,
    role       text        not null check (role in ('owner', 'editor', 'viewer')),
    added_at   timestamptz not null default now(),
    primary key (project_id, user_id)
);
