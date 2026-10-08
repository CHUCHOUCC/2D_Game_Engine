insert into service_clients (name, audience) values
    ('AI service', 'ai-service')
on conflict (name) do nothing;
