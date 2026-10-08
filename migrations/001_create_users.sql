-- Accounts. Only a salted scrypt hash of the password is stored.
create table if not exists users (
    id            bigint generated always as identity primary key,
    username      text        not null check (length(username) between 1 and 50),
    email         text        not null unique check (length(email) <= 254),
    salt          bytea       not null,
    password_hash bytea       not null,
    created_at    timestamptz not null default now()
);
