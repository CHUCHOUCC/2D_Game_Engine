create table if not exists play_events (
    id              bigint generated always as identity primary key,
    play_session_id bigint  not null references play_sessions (id) on delete cascade,
    kind            text    not null,
    x               real,
    y               real,
    at_ms           integer not null default 0,
    details         jsonb   not null default '{}'::jsonb
);
