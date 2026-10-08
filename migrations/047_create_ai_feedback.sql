create table if not exists ai_feedback (
    id            bigint generated always as identity primary key,
    generation_id bigint      not null references ai_generations (id) on delete cascade,
    user_id       bigint      not null references users (id) on delete cascade,
    rating        smallint    not null check (rating between 1 and 5),
    comment       text        not null default '',
    created_at    timestamptz not null default now()
);
