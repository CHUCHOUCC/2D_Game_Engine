alter table projects add column if not exists created_at timestamptz not null default now();
