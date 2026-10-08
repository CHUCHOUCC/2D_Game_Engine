create table if not exists high_scores (
    id          bigint generated always as identity primary key,
    project_id  bigint      not null references projects (id) on delete cascade,
    user_id     bigint      not null references users (id) on delete cascade,
    score       integer     not null,
    achieved_at timestamptz not null default now()
);
