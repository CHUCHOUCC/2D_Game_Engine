create table if not exists user_roles (
    user_id    bigint      not null references users (id) on delete cascade,
    role_id    smallint    not null references roles (id) on delete cascade,
    granted_at timestamptz not null default now(),
    primary key (user_id, role_id)
);
