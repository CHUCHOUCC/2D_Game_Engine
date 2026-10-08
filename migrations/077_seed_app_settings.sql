insert into app_settings (key, value) values
    ('world', '{"width": 1600, "height": 960, "tile_size": 32}'::jsonb),
    ('auth',  '{"access_minutes": 15, "refresh_days": 7, "max_failed_logins": 5}'::jsonb)
on conflict (key) do nothing;
