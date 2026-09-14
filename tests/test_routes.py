"""Tests for Flask routes, validation, and API endpoints."""

from __future__ import annotations

import pytest

from app import app, parse_compare_ids
from database import DATABASE_PATH, init_db


@pytest.fixture(scope="session", autouse=True)
def ensure_database():
    init_db(DATABASE_PATH, seed=True)


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_parse_compare_ids_valid():
    ids, error = parse_compare_ids("1,2,3")
    assert error is None
    assert ids == [1, 2, 3]


def test_parse_compare_ids_too_few():
    ids, error = parse_compare_ids("1")
    assert ids == []
    assert error is not None


def test_parse_compare_ids_too_many():
    ids, error = parse_compare_ids("1,2,3,4")
    assert ids == []
    assert "at most" in error.lower()


def test_parse_compare_ids_invalid_token():
    ids, error = parse_compare_ids("1,abc")
    assert ids == []
    assert "invalid" in error.lower()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CompCompare" in response.data
    assert b"Compare Components" in response.data
    assert b"Search component" in response.data


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About CompCompare" in response.data


def test_components_page(client):
    response = client.get("/components")
    assert response.status_code == 200
    assert b"Component catalog" in response.data


def test_components_category_filter(client):
    response = client.get("/components?category=LED")
    assert response.status_code == 200
    assert b"LED" in response.data


def test_components_sort(client):
    response = client.get("/components?sort=name_asc")
    assert response.status_code == 200
    assert b"Component catalog" in response.data


def test_components_unknown_category_flashes(client):
    response = client.get("/components?category=NotReal", follow_redirects=True)
    assert response.status_code == 200
    assert b"Unknown category" in response.data


def test_component_detail(client):
    response = client.get("/component/1")
    assert response.status_code == 200
    assert b"Key specifications" in response.data
    assert b"Advantages" in response.data
    assert b"Real-world suggestion" in response.data


def test_component_detail_missing(client):
    response = client.get("/component/99999")
    assert response.status_code == 404


def test_compare_page_empty(client):
    response = client.get("/compare")
    assert response.status_code == 200
    assert b"Nothing to compare yet" in response.data or b"comparison" in response.data.lower()


def test_compare_two_components(client):
    response = client.get("/compare?ids=1,2")
    assert response.status_code == 200
    assert b"Attribute" in response.data
    assert b"compare-table" in response.data
    assert b"spec-card" in response.data


def test_compare_three_components(client):
    response = client.get("/compare?ids=1,2,3")
    assert response.status_code == 200
    assert b"Comparing" in response.data


def test_compare_invalid_redirects(client):
    response = client.get("/compare?ids=1", follow_redirects=True)
    assert response.status_code == 200
    assert b"at least" in response.data.lower()


def test_api_components(client):
    response = client.get("/api/components")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] >= 15
    assert isinstance(payload["components"], list)
    first = payload["components"][0]
    assert "name" in first
    assert "key_spec_list" in first
    assert "image_file" in first


def test_api_components_search(client):
    response = client.get("/api/components?q=MOSFET")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] >= 1


def test_api_compare_validate_ok(client):
    response = client.post("/api/compare/validate", json={"ids": [1, 2]})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert "url" in payload


def test_api_compare_validate_rejects_one(client):
    response = client.post("/api/compare/validate", json={"ids": [1]})
    assert response.status_code == 400
    assert response.get_json()["ok"] is False


def test_404_page(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    assert b"404" in response.data
