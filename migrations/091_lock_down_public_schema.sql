-- Lock the database down for anything that is not this API.
--
-- The API connects as the owner of the tables, so nothing changes for it. But a
-- hosted Postgres such as Supabase also publishes every table of the "public"
-- schema through its own REST API to the roles "anon" and "authenticated".
-- Row level security with no policy refuses every row to those roles, and the
-- grants are taken back too, so only the API can read or write the data.
do $$
declare
    t record;
begin
    for t in select tablename from pg_tables where schemaname = 'public' loop
        execute format('alter table public.%I enable row level security', t.tablename);
    end loop;
    if exists (select 1 from pg_roles where rolname = 'anon') then
        execute 'revoke all on all tables in schema public from anon';
        execute 'revoke all on all sequences in schema public from anon';
        execute 'revoke all on all functions in schema public from anon';
        execute 'alter default privileges in schema public revoke all on tables from anon';
        execute 'alter default privileges in schema public revoke all on sequences from anon';
        execute 'alter default privileges in schema public revoke all on functions from anon';
    end if;
    if exists (select 1 from pg_roles where rolname = 'authenticated') then
        execute 'revoke all on all tables in schema public from authenticated';
        execute 'revoke all on all sequences in schema public from authenticated';
        execute 'revoke all on all functions in schema public from authenticated';
        execute 'alter default privileges in schema public revoke all on tables from authenticated';
        execute 'alter default privileges in schema public revoke all on sequences from authenticated';
        execute 'alter default privileges in schema public revoke all on functions from authenticated';
    end if;
end
$$;
