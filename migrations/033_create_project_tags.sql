create table if not exists project_tags (
    project_id bigint  not null references projects (id) on delete cascade,
    tag_id     integer not null references tags (id) on delete cascade,
    primary key (project_id, tag_id)
);
