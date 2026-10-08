create table if not exists tilesets (
    id          integer generated always as identity primary key,
    pack_id     smallint not null references texture_packs (id) on delete cascade,
    name        text     not null,
    image_path  text     not null,
    tile_width  smallint not null default 32,
    tile_height smallint not null default 32,
    columns     smallint not null default 1
);
