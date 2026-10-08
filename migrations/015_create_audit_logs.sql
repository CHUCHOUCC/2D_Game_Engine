-- Who did what and when (login, logout, project changes).
create table if not exists audit_logs (
    id          bigint generated always as identity primary key,
    user_id     bigint      references users (id) on delete set null,
    action      text        not null,
    entity_type text        not null default '',
    entity_id   text        not null default '',
    details     jsonb       not null default '{}'::jsonb,
    ip_address  text        not null default '',
    created_at  timestamptz not null default now()
);
