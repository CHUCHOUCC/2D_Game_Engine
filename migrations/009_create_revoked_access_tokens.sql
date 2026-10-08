-- Access-token ids (JWT jti) revoked before they expire, for example on logout.
create table if not exists revoked_access_tokens (
    jti        text        primary key,
    user_id    bigint      not null references users (id) on delete cascade,
    expires_at timestamptz not null,
    revoked_at timestamptz not null default now()
);
