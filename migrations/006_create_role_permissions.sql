create table if not exists role_permissions (
    role_id       smallint not null references roles (id) on delete cascade,
    permission_id smallint not null references permissions (id) on delete cascade,
    primary key (role_id, permission_id)
);
