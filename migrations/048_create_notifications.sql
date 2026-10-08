create table if not exists notifications (
    id         bigint generated always as identity primary key,
    user_id    bigint      not null references users (id) on delete cascade,
    kind       text        not null,
    message    text        not null,
    read_at    timestamptz,
    created_at timestamptz not null default now()
);
