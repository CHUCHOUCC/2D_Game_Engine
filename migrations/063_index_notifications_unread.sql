create index if not exists notifications_unread_idx on notifications (user_id) where read_at is null;
