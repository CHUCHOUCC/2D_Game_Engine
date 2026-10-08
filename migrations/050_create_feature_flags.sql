create table if not exists feature_flags (
    code        text    primary key,
    enabled     boolean not null default false,
    description text    not null default ''
);
