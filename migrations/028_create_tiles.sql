create table if not exists tiles (
    id         integer generated always as identity primary key,
    tileset_id integer  not null references tilesets (id) on delete cascade,
    tile_index smallint not null,
    solid      boolean  not null default false,
    properties jsonb    not null default '{}'::jsonb,
    unique (tileset_id, tile_index)
);
