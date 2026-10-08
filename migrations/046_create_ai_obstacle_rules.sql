-- Per-kind weights the AI uses when it places new obstacles.
create table if not exists ai_obstacle_rules (
    id           bigint generated always as identity primary key,
    ai_model_id  bigint      not null references ai_models (id) on delete cascade,
    kind         text        not null references object_kinds (code),
    weight       real        not null default 1 check (weight >= 0),
    min_distance real        not null default 64,
    max_count    integer     not null default 10,
    updated_at   timestamptz not null default now(),
    unique (ai_model_id, kind)
);
