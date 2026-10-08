create table if not exists ai_requests (
    id          bigint generated always as identity primary key,
    project_id  bigint      not null references projects (id) on delete cascade,
    user_id     bigint      not null references users (id) on delete cascade,
    prompt      text        not null,
    status      text        not null check (status in ('ok', 'error')),
    error       text        not null default '',
    duration_ms integer     not null default 0,
    created_at  timestamptz not null default now()
);
