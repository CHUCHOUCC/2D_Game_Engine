-- Internal services allowed to receive service tokens (the AI service).
create table if not exists service_clients (
    id         smallint generated always as identity primary key,
    name       text        not null unique,
    audience   text        not null unique,
    enabled    boolean     not null default true,
    created_at timestamptz not null default now()
);
