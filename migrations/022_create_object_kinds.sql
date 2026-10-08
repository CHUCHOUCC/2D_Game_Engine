-- Catalogue of the object kinds the editor and the game understand.
create table if not exists object_kinds (
    code        text    primary key,
    name        text    not null,
    category    text    not null check (category in ('obstacle', 'collectible', 'enemy', 'building', 'decoration', 'player')),
    solid       boolean not null default false,
    movable     boolean not null default false,
    collectible boolean not null default false,
    hostile     boolean not null default false
);
