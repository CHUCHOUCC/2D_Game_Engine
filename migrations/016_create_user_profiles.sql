create table if not exists user_profiles (
    user_id      bigint primary key references users (id) on delete cascade,
    display_name text   not null default '',
    avatar_url   text   not null default '',
    bio          text   not null default '' check (length(bio) <= 500),
    country      text   not null default ''
);
