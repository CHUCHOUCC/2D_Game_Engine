create table if not exists enemy_types (
    id           smallint generated always as identity primary key,
    code         text     not null unique,
    name         text     not null,
    health       smallint not null check (health > 0),
    speed        real     not null check (speed >= 0),
    damage       smallint not null check (damage >= 0),
    behavior     text     not null check (behavior in ('chase', 'patrol', 'idle')),
    texture_code text     not null
);
