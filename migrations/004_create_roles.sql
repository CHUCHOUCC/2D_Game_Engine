-- Roles a user can have (player, creator, admin).
create table if not exists roles (
    id          smallint generated always as identity primary key,
    name        text not null unique,
    description text not null default ''
);
