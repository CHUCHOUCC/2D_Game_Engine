create table if not exists email_verification_tokens (
    id          bigint generated always as identity primary key,
    user_id     bigint      not null references users (id) on delete cascade,
    token_hash  text        not null unique,
    expires_at  timestamptz not null,
    verified_at timestamptz,
    created_at  timestamptz not null default now()
);
