create table if not exists textures (
    id        integer generated always as identity primary key,
    pack_id   smallint not null references texture_packs (id) on delete cascade,
    code      text     not null,
    kind      text     references object_kinds (code),
    file_path text     not null,
    width     smallint not null,
    height    smallint not null,
    frames    smallint not null default 1,
    unique (pack_id, code)
);
