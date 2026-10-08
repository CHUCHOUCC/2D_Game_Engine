create index if not exists login_attempts_email_time_idx on login_attempts (email, attempted_at desc);
