create table if not exists achievements (
    id          smallint generated always as identity primary key,
    code        text     not null unique,
    name        text     not null,
    description text     not null,
    points      smallint not null default 10
);
