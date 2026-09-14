"""
Built-in circuit lab problems for the interactive simulator.
No hardware — pure educational browser simulation.
"""

from __future__ import annotations

import re
from typing import Any

LAB_PARTS = (
    {
        "id": "battery",
        "name": "Battery 9V",
        "icon": "battery",
        "hint": "Provides voltage for the circuit.",
    },
    {
        "id": "resistor",
        "name": "Resistor 220Ω",
        "icon": "resistor",
        "hint": "Limits current so the LED stays safe.",
    },
    {
        "id": "led",
        "name": "LED (forward)",
        "icon": "led",
        "hint": "Lights when current flows with correct polarity.",
        "polarity": "forward",
    },
    {
        "id": "led_rev",
        "name": "LED (reversed)",
        "icon": "led",
        "hint": "Reversed LED blocks DC current.",
        "polarity": "reverse",
    },
    {
        "id": "lcd",
        "name": "LCD display",
        "icon": "lcd",
        "hint": "Shows text from the Program panel (lcd.print).",
    },
)

LAB_PROBLEMS: list[dict[str, Any]] = [
    {
        "id": "p1",
        "number": 1,
        "title": "Light the LED",
        "goal": "Build a safe series circuit so the LED blinks when you press Run.",
        "hint": "Use Battery → Resistor → LED (forward) in that order.",
        "slots": 3,
        "success_rule": "series_safe_led",
        "success_message": "Great! Current flows: Battery → Resistor → LED. The LED blinks.",
        "palette": ["battery", "resistor", "led", "led_rev"],
        "mode": "led",
    },
    {
        "id": "p2",
        "number": 2,
        "title": "Missing resistor trap",
        "goal": "Try connecting Battery and LED only, then fix it with a resistor.",
        "hint": "Battery + LED with no resistor should show an error. Add 220Ω to pass.",
        "slots": 3,
        "success_rule": "series_safe_led",
        "success_message": "Fixed! The resistor protects the LED from excess current.",
        "palette": ["battery", "resistor", "led", "led_rev"],
        "mode": "led",
    },
    {
        "id": "p3",
        "number": 3,
        "title": "LED polarity",
        "goal": "Discover why a reversed LED does not light, then place it forward.",
        "hint": "LED (reversed) in the chain fails. Swap to LED (forward).",
        "slots": 3,
        "success_rule": "series_safe_led",
        "success_message": "Correct polarity! Anode toward the more positive side of the path.",
        "palette": ["battery", "resistor", "led", "led_rev"],
        "mode": "led",
    },
    {
        "id": "p4",
        "number": 4,
        "title": "Order the series path",
        "goal": "Place Battery, Resistor, and forward LED in a clear series path and Run.",
        "hint": "Any series order with Battery + Resistor + forward LED (no reverse LED) works.",
        "slots": 3,
        "success_rule": "series_safe_led_any_order",
        "success_message": "Series path complete. The LED blinks safely.",
        "palette": ["battery", "resistor", "led", "led_rev"],
        "mode": "led",
    },
    {
        "id": "p5",
        "number": 5,
        "title": "Hello on LCD",
        "goal": "Wire Battery + Resistor + LCD, then print a message from the Program panel.",
        "hint": 'Circuit: Battery → Resistor → LCD. Program: lcd.print("Hello")',
        "slots": 3,
        "success_rule": "series_lcd",
        "success_message": "LCD powered and program OK — message shown on the display.",
        "palette": ["battery", "resistor", "lcd", "led"],
        "mode": "lcd",
        "sample_program": 'lcd.print("Hello ECE")',
    },
    {
        "id": "custom",
        "number": 0,
        "title": "Custom build",
        "goal": "Build LED or LCD circuits. For LCD, write lcd.print(\"...\") on the right.",
        "hint": "LED: Battery+Resistor+LED. LCD: Battery+Resistor+LCD + lcd.print(\"text\").",
        "slots": 4,
        "success_rule": "custom_led_or_lcd",
        "success_message": "Custom circuit OK!",
        "palette": ["battery", "resistor", "led", "led_rev", "lcd"],
        "mode": "auto",
        "sample_program": 'lcd.print("Custom")',
    },
]

_PRINT_RE = re.compile(
    r"""^\s*lcd\.print\(\s*(?P<quote>["'])(?P<text>.*?)(?P=quote)\s*\)\s*$""",
    re.IGNORECASE,
)
_CLEAR_RE = re.compile(r"^\s*lcd\.clear\(\s*\)\s*$", re.IGNORECASE)
_MAX_LCD_CHARS = 16


def get_lab_problem(problem_id: str) -> dict[str, Any] | None:
    for problem in LAB_PROBLEMS:
        if problem["id"] == problem_id:
            return problem
    return None


def get_lab_payload() -> dict[str, Any]:
    return {"parts": list(LAB_PARTS), "problems": list(LAB_PROBLEMS)}


def parse_lcd_program(program: str | None) -> dict[str, Any]:
    """
    Safe mini-parser for lcd.print("...") / lcd.clear().
    Does not execute real Python.
    """
    if program is None or not str(program).strip():
        return {
            "ok": False,
            "action": None,
            "text": "",
            "message": 'Program is empty. Try: lcd.print("Hello")',
        }

    lines = []
    for raw in str(program).splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)

    if not lines:
        return {
            "ok": False,
            "action": None,
            "text": "",
            "message": 'No commands found. Try: lcd.print("Hello")',
        }

    if len(lines) > 3:
        return {
            "ok": False,
            "action": None,
            "text": "",
            "message": "Keep the program short (max 3 command lines).",
        }

    # Use the last meaningful command
    command = lines[-1]
    clear_match = _CLEAR_RE.match(command)
    if clear_match:
        return {
            "ok": True,
            "action": "clear",
            "text": "",
            "message": "LCD cleared.",
        }

    print_match = _PRINT_RE.match(command)
    if print_match:
        text = print_match.group("text")
        if len(text) > _MAX_LCD_CHARS:
            return {
                "ok": False,
                "action": None,
                "text": "",
                "message": f"Message too long (max {_MAX_LCD_CHARS} characters).",
            }
        return {
            "ok": True,
            "action": "print",
            "text": text,
            "message": "Message ready for LCD.",
        }

    return {
        "ok": False,
        "action": None,
        "text": "",
        "message": (
            'Unknown command. Allowed: lcd.print("text") or lcd.clear()'
        ),
    }


def validate_circuit(
    problem_id: str,
    slots: list[str] | None,
    program: str | None = None,
) -> dict[str, Any]:
    """
    Validate a series slot chain (and optional LCD program).
    Returns {ok, message, blink, lcd_text, lcd_action}.
    """
    problem = get_lab_problem(problem_id)
    if problem is None:
        return {
            "ok": False,
            "blink": False,
            "lcd_text": "",
            "lcd_action": None,
            "message": "Unknown problem. Pick one from the left panel.",
        }

    raw = slots if isinstance(slots, list) else []
    chain = [str(item).strip() for item in raw if str(item).strip()]
    valid_ids = {part["id"] for part in LAB_PARTS}
    for item in chain:
        if item not in valid_ids:
            return {
                "ok": False,
                "blink": False,
                "lcd_text": "",
                "lcd_action": None,
                "message": f"Unknown part in circuit: {item}.",
            }

    if not chain:
        return {
            "ok": False,
            "blink": False,
            "lcd_text": "",
            "lcd_action": None,
            "message": "Circuit is empty. Drag parts into the slots, then click Run.",
        }

    counts = {pid: chain.count(pid) for pid in valid_ids}
    has_battery = counts.get("battery", 0) >= 1
    has_resistor = counts.get("resistor", 0) >= 1
    led_count = counts.get("led", 0)
    has_led = led_count >= 1
    has_led_rev = counts.get("led_rev", 0) >= 1
    has_lcd = counts.get("lcd", 0) >= 1
    rule = problem["success_rule"]

    # LCD strip while an LED-only problem is selected
    if has_lcd and rule in {"series_safe_led", "series_safe_led_any_order"}:
        return _fail(
            "You placed an LCD. Select problem 5 — Hello on LCD — on the left, then Run."
        )

    if has_led_rev and not has_led:
        return _fail("Error: LED is reversed — no light. Flip to LED (forward).")

    if has_led_rev and has_led:
        return _fail("Error: Remove the reversed LED. Keep only forward LED(s).")

    if not has_battery:
        return _fail("Error: No battery — the circuit has no power source.")

    # LED powered without resistor (only when an LED is actually in the strip)
    if has_battery and has_led and not has_resistor and not has_lcd:
        return _fail("Error: Missing resistor! LED can burn without current limiting.")

    # LCD without resistor
    if has_battery and has_lcd and not has_resistor:
        return _fail("Error: Add a resistor before the LCD module.")

    if rule == "series_safe_led":
        if has_battery and has_resistor and not has_led:
            return _fail("Error: Add a forward LED to see light when you Run.")
        expected = ["battery", "resistor", "led"]
        if chain == expected:
            return _ok_led(problem["success_message"])
        if sorted(chain) == sorted(expected) and len(chain) == 3:
            return _fail(
                "Almost! Use this order: Battery → Resistor → LED (forward)."
            )
        return _fail(
            "Error: Need Battery → Resistor → LED (forward) only, in that order."
        )

    if rule == "series_safe_led_any_order":
        if has_battery and has_resistor and not has_led:
            return _fail("Error: Add a forward LED to see light when you Run.")
        if (
            counts.get("battery", 0) == 1
            and counts.get("resistor", 0) == 1
            and led_count == 1
            and counts.get("led_rev", 0) == 0
            and counts.get("lcd", 0) == 0
            and len(chain) == 3
        ):
            return _ok_led(problem["success_message"])
        return _fail(
            "Error: Use exactly one Battery, one Resistor, and one forward LED."
        )

    if rule == "series_lcd":
        return _validate_lcd_circuit(counts, chain, program, problem)

    if rule == "custom_led_or_lcd":
        if has_lcd:
            return _validate_lcd_circuit(counts, chain, program, problem)
        if has_battery and has_resistor and not has_led:
            return _fail("Error: Add a forward LED, or use LCD + lcd.print(...).")
        if (
            counts.get("battery", 0) == 1
            and counts.get("resistor", 0) == 1
            and led_count == 1
            and counts.get("led_rev", 0) == 0
            and counts.get("lcd", 0) == 0
            and len(chain) == 3
        ):
            return _ok_led("Custom LED circuit OK — LED blinks!")
        return _fail(
            "Error: Build Battery+Resistor+LED, or Battery+Resistor+LCD with a program."
        )

    return _fail("Error: Circuit does not match this problem’s goal.")


def _validate_lcd_circuit(
    counts: dict[str, int],
    chain: list[str],
    program: str | None,
    problem: dict[str, Any],
) -> dict[str, Any]:
    if counts.get("lcd", 0) < 1:
        return _fail("Error: Drag an LCD into the series strip.")

    if counts.get("led", 0) > 0 or counts.get("led_rev", 0) > 0:
        return _fail("Error: For the LCD task, use Battery + Resistor + LCD only.")

    if not (
        counts.get("battery", 0) == 1
        and counts.get("resistor", 0) == 1
        and counts.get("lcd", 0) == 1
        and len(chain) == 3
    ):
        return _fail(
            "Error: Need exactly Battery + Resistor + LCD in the strip."
        )

    parsed = parse_lcd_program(program)
    if not parsed["ok"]:
        return {
            "ok": False,
            "blink": False,
            "lcd_text": "",
            "lcd_action": None,
            "message": parsed["message"],
        }

    return {
        "ok": True,
        "blink": False,
        "lcd_text": parsed.get("text", ""),
        "lcd_action": parsed.get("action"),
        "message": problem.get(
            "success_message", "LCD OK — message shown on the display."
        ),
    }


def _fail(message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "blink": False,
        "lcd_text": "",
        "lcd_action": None,
        "message": message,
    }


def _ok_led(message: str) -> dict[str, Any]:
    return {
        "ok": True,
        "blink": True,
        "lcd_text": "",
        "lcd_action": None,
        "message": message,
    }
