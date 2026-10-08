create table if not exists ai_generations (
    id           bigint generated always as identity primary key,
    request_id   bigint      not null references ai_requests (id) on delete cascade,
    object_count integer     not null,
    objects      jsonb       not null,
    difficulty   real        not null default 0.5,
    created_at   timestamptz not null default now()
);
