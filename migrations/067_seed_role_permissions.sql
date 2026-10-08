insert into role_permissions (role_id, permission_id)
select r.id, p.id
from roles r
join permissions p on
    (r.name = 'player'  and p.code = 'project.play') or
    (r.name = 'creator' and p.code in ('project.create', 'project.edit', 'project.delete', 'project.play', 'ai.generate')) or
    (r.name = 'admin')
on conflict do nothing;
