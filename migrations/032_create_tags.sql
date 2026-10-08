create table if not exists tags (
    id   integer generated always as identity primary key,
    name text not null unique check (length(name) between 1 and 30)
);
