create table if not exists sprite_animations (
    id          integer generated always as identity primary key,
    texture_id  integer  not null references textures (id) on delete cascade,
    name        text     not null,
    start_frame smallint not null,
    end_frame   smallint not null,
    frame_rate  smallint not null default 8,
    loops       boolean  not null default true,
    unique (texture_id, name),
    check (end_frame >= start_frame)
);
