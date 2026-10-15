-- What each 2D character says in a speech bubble when the player comes close.
create table if not exists character_lines (
    id   smallint generated always as identity primary key,
    kind text not null references object_kinds (code) on delete cascade,
    line text not null check (length(line) between 1 and 120),
    unique (kind, line)
);
