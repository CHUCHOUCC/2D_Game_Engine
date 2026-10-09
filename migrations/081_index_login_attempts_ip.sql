create index if not exists login_attempts_ip_time_idx on login_attempts (ip_address, attempted_at desc);
