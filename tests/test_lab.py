"""Tests for the interactive Circuit Lab."""

from __future__ import annotations

import pytest

from app import app
from lab_problems import parse_lcd_program, validate_circuit


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_lab_page(client):
    response = client.get("/lab")
    assert response.status_code == 200
    assert b"Circuit Lab" in response.data
    assert b"Hello on LCD" in response.data
    assert b"lcd.print" in response.data
    assert b"LCD display" in response.data


def test_lab_problem_route(client):
    response = client.get("/lab/p5")
    assert response.status_code == 200
    assert b"Hello on LCD" in response.data


def test_validate_success_ordered():
    result = validate_circuit("p1", ["battery", "resistor", "led"])
    assert result["ok"] is True
    assert result["blink"] is True


def test_validate_wrong_order_p1():
    result = validate_circuit("p1", ["led", "battery", "resistor"])
    assert result["ok"] is False
    assert "order" in result["message"].lower()


def test_validate_missing_resistor():
    result = validate_circuit("p2", ["battery", "led"])
    assert result["ok"] is False
    assert "resistor" in result["message"].lower()


def test_validate_reversed_led():
    result = validate_circuit("p3", ["battery", "resistor", "led_rev"])
    assert result["ok"] is False
    assert "reverse" in result["message"].lower()


def test_validate_any_order_p4():
    result = validate_circuit("p4", ["led", "resistor", "battery"])
    assert result["ok"] is True
    assert result["blink"] is True


def test_parse_lcd_print():
    parsed = parse_lcd_program('lcd.print("Hello")')
    assert parsed["ok"] is True
    assert parsed["action"] == "print"
    assert parsed["text"] == "Hello"


def test_parse_lcd_clear():
    parsed = parse_lcd_program("lcd.clear()")
    assert parsed["ok"] is True
    assert parsed["action"] == "clear"


def test_parse_lcd_rejects_bad_command():
    parsed = parse_lcd_program("print('hi')")
    assert parsed["ok"] is False


def test_validate_lcd_success():
    result = validate_circuit(
        "p5",
        ["battery", "resistor", "lcd"],
        'lcd.print("Hello ECE")',
    )
    assert result["ok"] is True
    assert result["lcd_action"] == "print"
    assert result["lcd_text"] == "Hello ECE"
    assert result["blink"] is False


def test_lcd_on_led_problem_guides_user():
    result = validate_circuit(
        "p1",
        ["battery", "resistor", "lcd"],
        'lcd.print("Hello")',
    )
    assert result["ok"] is False
    assert "problem 5" in result["message"].lower()


def test_api_lab_run_lcd(client):
    response = client.post(
        "/api/lab/run",
        json={
            "problem_id": "p5",
            "slots": ["battery", "resistor", "lcd"],
            "program": 'lcd.print("Hi")',
        },
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["lcd_text"] == "Hi"


def test_api_lab_run_error(client):
    response = client.post(
        "/api/lab/run",
        json={"problem_id": "custom", "slots": ["battery", "led"]},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is False
    assert payload["blink"] is False
