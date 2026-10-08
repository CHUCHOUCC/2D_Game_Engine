-- Keyboard shortcuts a user customised in the editor.
create table if not exists editor_shortcuts (
    user_id bigint not null references users (id) on delete cascade,
    action  text   not null,
    keys    text   not null,
    primary key (user_id, action)
);
