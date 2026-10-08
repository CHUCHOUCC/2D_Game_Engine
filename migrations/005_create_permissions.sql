-- Fine-grained permissions, granted to roles.
create table if not exists permissions (
    id          smallint generated always as identity primary key,
    code        text not null unique,
    description text not null default ''
);
