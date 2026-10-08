create index if not exists audit_logs_user_time_idx on audit_logs (user_id, created_at desc);
