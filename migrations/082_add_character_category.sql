-- 2D characters (villager, knight, wizard) get their own category.
alter table object_kinds drop constraint if exists object_kinds_category_check;
alter table object_kinds add constraint object_kinds_category_check
    check (category in ('obstacle', 'collectible', 'enemy', 'building', 'decoration', 'player', 'character'));
