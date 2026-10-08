create table if not exists user_achievements (
    user_id        bigint      not null references users (id) on delete cascade,
    achievement_id smallint    not null references achievements (id) on delete cascade,
    unlocked_at    timestamptz not null default now(),
    primary key (user_id, achievement_id)
);
