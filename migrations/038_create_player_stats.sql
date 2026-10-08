-- Running totals per player, updated when a run ends.
create table if not exists player_stats (
    user_id          bigint      primary key references users (id) on delete cascade,
    games_played     integer     not null default 0,
    games_won        integer     not null default 0,
    total_score      bigint      not null default 0,
    best_score       integer     not null default 0,
    coins_collected  bigint      not null default 0,
    enemies_defeated bigint      not null default 0,
    deaths           bigint      not null default 0,
    play_time_ms     bigint      not null default 0,
    updated_at       timestamptz not null default now()
);
