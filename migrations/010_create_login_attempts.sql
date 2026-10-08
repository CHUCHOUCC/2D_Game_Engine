-- Every login attempt, used to slow down password guessing.
create table if not exists login_attempts (
    id           bigint generated always as identity primary key,
    email        text        not null,
    ip_address   text        not null default '',
    succeeded    boolean     not null,
    attempted_at timestamptz not null default now()
);
