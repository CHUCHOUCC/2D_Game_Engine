-- Personal API keys for scripts and tools. Only the hash is stored.
create table if not exists api_keys (
    id           bigint generated always as identity primary key,
    user_id      bigint      not null references users (id) on delete cascade,
    name         text        not null,
    prefix       text        not null,
    key_hash     text        not null unique,
    scopes       text[]      not null default '{}',
    created_at   timestamptz not null default now(),
    last_used_at timestamptz,
    revoked_at   timestamptz
);
