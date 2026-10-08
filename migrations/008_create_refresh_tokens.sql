-- Refresh tokens. Each login starts a family; every refresh rotates the token
-- inside its family. Reusing a rotated token revokes the whole family.
create table if not exists refresh_tokens (
    id          bigint generated always as identity primary key,
    user_id     bigint      not null references users (id) on delete cascade,
    token_hash  text        not null unique,
    family_id   uuid        not null,
    issued_at   timestamptz not null default now(),
    expires_at  timestamptz not null,
    revoked_at  timestamptz,
    replaced_by bigint      references refresh_tokens (id) on delete set null,
    user_agent  text        not null default ''
);
