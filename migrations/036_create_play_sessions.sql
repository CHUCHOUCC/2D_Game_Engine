-- One run of the game (Jugar). The AI learns from these numbers.
create table if not exists play_sessions (
    id               bigint generated always as identity primary key,
    project_id       bigint      not null references projects (id) on delete cascade,
    player_id        bigint      not null references users (id) on delete cascade,
    started_at       timestamptz not null default now(),
    ended_at         timestamptz,
    outcome          text        check (outcome in ('won', 'lost', 'quit')),
    score            integer     not null default 0,
    coins_collected  integer     not null default 0,
    coins_total      integer     not null default 0,
    enemies_defeated integer     not null default 0,
    damage_taken     integer     not null default 0,
    deaths           integer     not null default 0,
    duration_ms      integer     not null default 0,
    difficulty       real        not null default 0.5
);
