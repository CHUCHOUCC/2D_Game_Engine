insert into permissions (code, description) values
    ('project.create', 'Create projects'),
    ('project.edit',   'Edit own projects'),
    ('project.delete', 'Delete own projects'),
    ('project.play',   'Play a project'),
    ('ai.generate',    'Ask the AI for objects'),
    ('admin.users',    'Manage users')
on conflict (code) do nothing;
