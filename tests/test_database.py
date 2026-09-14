"""Tests for database initialization, seeding, and queries."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from database import (
    CATEGORIES,
    SAMPLE_COMPONENTS,
    get_all_components,
    get_category_counts,
    get_component_by_id,
    get_component_count,
    get_components_by_ids,
    init_db,
)


@pytest.fixture()
def temp_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test_components.db"
    init_db(db_path, seed=True)
    return db_path


def test_init_db_creates_file_and_schema(temp_db: Path):
    assert temp_db.exists()
    conn = sqlite3.connect(temp_db)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='components'"
        ).fetchall()
        assert tables
    finally:
        conn.close()


def test_seed_inserts_at_least_fifteen_components(temp_db: Path):
    count = get_component_count(temp_db)
    assert count >= 15
    assert count == len(SAMPLE_COMPONENTS)


def test_seed_is_idempotent(temp_db: Path):
    first = get_component_count(temp_db)
    init_db(temp_db, seed=True)
    second = get_component_count(temp_db)
    assert first == second


def test_categories_cover_required_types(temp_db: Path):
    rows = get_all_components(temp_db)
    found = {row["category"] for row in rows}
    for category in CATEGORIES:
        assert category in found


def test_get_all_components_filter_by_category(temp_db: Path):
    resistors = get_all_components(temp_db, category="Resistor")
    assert resistors
    assert all(row["category"] == "Resistor" for row in resistors)


def test_get_all_components_search(temp_db: Path):
    results = get_all_components(temp_db, search="555")
    assert results
    assert any("555" in row["name"] or "555" in row["part_number"] for row in results)


def test_get_all_components_sort_name(temp_db: Path):
    rows = get_all_components(temp_db, sort="name_asc")
    names = [row["name"] for row in rows]
    assert names == sorted(names)


def test_components_have_key_specs_and_images(temp_db: Path):
    rows = get_all_components(temp_db)
    assert rows
    assert rows[0]["key_specs"]
    assert rows[0]["image_slug"]
    assert rows[0]["suggestion"]


def test_get_component_by_id(temp_db: Path):
    row = get_component_by_id(1, temp_db)
    assert row is not None
    assert row["id"] == 1
    assert get_component_by_id(99999, temp_db) is None


def test_get_components_by_ids_preserves_order(temp_db: Path):
    rows = get_components_by_ids([3, 1, 2], temp_db)
    assert [row["id"] for row in rows] == [3, 1, 2]


def test_category_counts(temp_db: Path):
    counts = get_category_counts(temp_db)
    assert counts
    total = sum(row["count"] for row in counts)
    assert total == get_component_count(temp_db)
