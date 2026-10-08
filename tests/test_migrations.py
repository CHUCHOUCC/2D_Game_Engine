"""Tests for the migration runner.

The ordering tests need no database. The last test runs every migration on a
real PostgreSQL when TEST_DATABASE_URL is set (a throw-away database only).
"""
import os

import psycopg
import pytest
from psycopg.rows import dict_row

from app.migrate import MIGRATIONS_DIR, apply_pending, migration_files


def test_migration_files_are_numbered_and_sorted():
    names = [path.stem for path in migration_files()]
    assert names == sorted(names)
    assert all(name[:3].isdigit() and name[3] == "_" for name in names)


def test_migration_numbers_are_unique():
    numbers = [path.stem[:3] for path in migration_files()]
    assert len(numbers) == len(set(numbers))


def test_the_schema_defines_more_than_forty_tables():
    sql = " ".join(path.read_text(encoding="utf-8") for path in migration_files())
    assert sql.count("create table if not exists") > 40


def test_every_migration_is_idempotent_sql():
    for path in migration_files(MIGRATIONS_DIR):
        text = path.read_text(encoding="utf-8").lower()
        if "create table" in text:
            assert "if not exists" in text, path.name
        if "insert into" in text:
            assert "on conflict" in text, path.name


DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


@pytest.mark.skipif(DATABASE_URL is None, reason="TEST_DATABASE_URL is not set")
def test_apply_pending_runs_everything_once():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row, prepare_threshold=None) as connection:
        apply_pending(connection)
        assert apply_pending(connection) == []
        count = connection.execute(
            "select count(*) as n from information_schema.tables where table_schema = 'public'"
        ).fetchone()["n"]
        assert count > 40
