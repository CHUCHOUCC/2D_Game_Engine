-- Legacy opaque-token sessions (kept so existing deployments keep working).
create table if not exists sessions (
    token_hash text        primary key,
    user_id    bigint      not null references users (id) on delete cascade,
    expires_at timestamptz not null
);
