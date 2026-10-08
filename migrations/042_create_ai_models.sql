-- What the AI has learned for one project: the parameters of its level model.
create table if not exists ai_models (
    id           bigint generated always as identity primary key,
    project_id   bigint      not null unique references projects (id) on delete cascade,
    version      integer     not null default 1,
    parameters   jsonb       not null default '{}'::jsonb,
    samples_seen integer     not null default 0,
    updated_at   timestamptz not null default now()
);
