create table if not exists texture_packs (
    id         smallint generated always as identity primary key,
    code       text        not null unique,
    name       text        not null,
    author     text        not null default '',
    license    text        not null default '',
    created_at timestamptz not null default now()
);
