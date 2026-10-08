-- Starter scenes users can clone into a new project.
create table if not exists level_templates (
    id          smallint generated always as identity primary key,
    code        text        not null unique,
    name        text        not null,
    description text        not null default '',
    scene       jsonb       not null,
    created_at  timestamptz not null default now()
);
