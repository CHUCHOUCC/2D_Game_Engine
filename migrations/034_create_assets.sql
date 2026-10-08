-- Files uploaded by users (images, sounds).
create table if not exists assets (
    id           bigint generated always as identity primary key,
    owner_id     bigint      not null references users (id) on delete cascade,
    project_id   bigint      references projects (id) on delete cascade,
    file_name    text        not null,
    mime_type    text        not null,
    size_bytes   bigint      not null check (size_bytes >= 0),
    storage_path text        not null,
    created_at   timestamptz not null default now()
);
