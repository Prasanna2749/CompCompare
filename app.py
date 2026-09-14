"""
Electronic Component Comparison Web Application
Flask backend with SQLite storage, search, filtering, sorting, and compare.
"""

from __future__ import annotations

import os
import re
from typing import Any

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from database import (
    CATEGORIES,
    HOME_CATEGORIES,
    SORT_OPTIONS,
    enrich_component,
    get_all_components,
    get_category_counts,
    get_component_by_id,
    get_component_count,
    get_components_by_ids,
    get_showcase_components,
    init_db,
    row_to_dict,
)
from lab_problems import get_lab_payload, get_lab_problem, validate_circuit

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ece-component-compare-dev-key")

MAX_COMPARE = 3
MIN_COMPARE = 2


def parse_compare_ids(raw: str | None) -> tuple[list[int], str | None]:
    """Validate and parse comma-separated component IDs for comparison."""
    if raw is None or not str(raw).strip():
        return [], "Select at least two components to compare."

    parts = [p.strip() for p in str(raw).split(",") if p.strip()]
    if not parts:
        return [], "Select at least two components to compare."

    ids: list[int] = []
    seen: set[int] = set()
    for part in parts:
        if not re.fullmatch(r"\d+", part):
            return [], f"Invalid component id: {part!r}."
        value = int(part)
        if value <= 0:
            return [], f"Invalid component id: {value}."
        if value in seen:
            continue
        seen.add(value)
        ids.append(value)

    if len(ids) < MIN_COMPARE:
        return [], f"Select at least {MIN_COMPARE} components to compare."
    if len(ids) > MAX_COMPARE:
        return [], f"You can compare at most {MAX_COMPARE} components at once."

    return ids, None


def enrich_many(rows) -> list[dict[str, Any]]:
    return [enrich_component(row) for row in rows if row is not None]


@app.context_processor
def inject_globals() -> dict[str, Any]:
    return {
        "categories": CATEGORIES,
        "home_categories": HOME_CATEGORIES,
        "max_compare": MAX_COMPARE,
        "sort_options": SORT_OPTIONS,
    }


@app.route("/")
def index():
    """Poster-style home: search, category icons, showcase comparison cards."""
    counts = get_category_counts()
    total = get_component_count()
    showcase = enrich_many(get_showcase_components())
    return render_template(
        "index.html",
        category_counts=counts,
        total_components=total,
        showcase=showcase,
    )


@app.route("/about")
def about():
    """About page describing purpose and audience."""
    return render_template("about.html")


@app.route("/components")
def components():
    """Browse components with category filter, search, and sort."""
    category = request.args.get("category", "all").strip() or "all"
    search = request.args.get("q", "").strip()
    sort = request.args.get("sort", "category").strip() or "category"

    if category.lower() != "all" and category not in CATEGORIES:
        flash("Unknown category. Showing all components.", "warning")
        category = "all"

    if sort not in SORT_OPTIONS:
        flash("Unknown sort option. Using category order.", "warning")
        sort = "category"

    if len(search) > 100:
        flash("Search query is too long (max 100 characters).", "warning")
        search = search[:100]

    items = enrich_many(
        get_all_components(
            category=None if category.lower() == "all" else category,
            search=search or None,
            sort=sort,
        )
    )
    return render_template(
        "components.html",
        components=items,
        active_category=category,
        search_query=search,
        active_sort=sort,
        result_count=len(items),
    )


@app.route("/component/<int:component_id>")
def component_detail(component_id: int):
    """Detailed view for a single component."""
    if component_id <= 0:
        abort(404)
    component = enrich_component(get_component_by_id(component_id))
    if component is None:
        abort(404)

    related = enrich_many(
        [
            c
            for c in get_all_components(category=component["category"])
            if c["id"] != component["id"]
        ][:4]
    )

    return render_template(
        "component_detail.html",
        component=component,
        related=related,
    )


@app.route("/compare")
def compare():
    """Side-by-side comparison of 2–3 components (cards + table)."""
    raw_ids = request.args.get("ids", "")
    ids, error = parse_compare_ids(raw_ids)

    if error and raw_ids.strip():
        flash(error, "error")
        return redirect(url_for("components"))

    if error:
        return render_template(
            "compare.html",
            components=[],
            compare_fields=[],
            selected_ids=[],
            error=error,
        )

    selected = enrich_many(get_components_by_ids(ids))
    if len(selected) < MIN_COMPARE:
        flash(
            "One or more selected components were not found. Please choose again.",
            "error",
        )
        return redirect(url_for("components"))

    compare_fields = [
        ("Category", "category"),
        ("Type", "component_type"),
        ("Part Number", "part_number"),
        ("Manufacturer", "manufacturer"),
        ("Description", "description"),
        ("Specifications", "specifications"),
        ("Applications", "applications"),
        ("Advantages", "advantages"),
        ("Disadvantages", "disadvantages"),
        ("Common Uses", "common_uses"),
        ("Real-world suggestion", "suggestion"),
    ]

    return render_template(
        "compare.html",
        components=selected,
        compare_fields=compare_fields,
        selected_ids=[c["id"] for c in selected],
        error=None,
    )


@app.route("/api/components")
def api_components():
    """JSON API for live search/filter/sort used by the front-end."""
    category = request.args.get("category", "all").strip() or "all"
    search = request.args.get("q", "").strip()
    sort = request.args.get("sort", "category").strip() or "category"

    if len(search) > 100:
        return jsonify({"error": "Search query too long.", "components": []}), 400

    if category.lower() != "all" and category not in CATEGORIES:
        return jsonify({"error": "Unknown category.", "components": []}), 400

    if sort not in SORT_OPTIONS:
        return jsonify({"error": "Unknown sort option.", "components": []}), 400

    items = get_all_components(
        category=None if category.lower() == "all" else category,
        search=search or None,
        sort=sort,
    )
    payload = [row_to_dict(row) for row in items]
    return jsonify({"count": len(payload), "components": payload})


@app.route("/api/compare/validate", methods=["POST"])
def api_compare_validate():
    """Validate comparison selection before navigating."""
    data = request.get_json(silent=True) or {}
    raw_ids = data.get("ids", "")
    if isinstance(raw_ids, list):
        raw_ids = ",".join(str(i) for i in raw_ids)

    ids, error = parse_compare_ids(str(raw_ids))
    if error:
        return jsonify({"ok": False, "error": error}), 400

    selected = get_components_by_ids(ids)
    if len(selected) < MIN_COMPARE:
        return jsonify({"ok": False, "error": "One or more components were not found."}), 404

    return jsonify(
        {
            "ok": True,
            "ids": [c["id"] for c in selected],
            "url": url_for("compare", ids=",".join(str(c["id"]) for c in selected)),
        }
    )


@app.route("/lab")
@app.route("/lab/<problem_id>")
def lab(problem_id: str = "p1"):
    """Interactive circuit lab: drag parts, Run to blink LED or show error."""
    payload = get_lab_payload()
    active = get_lab_problem(problem_id) or get_lab_problem("p1")
    return render_template(
        "lab.html",
        lab_parts=payload["parts"],
        lab_problems=payload["problems"],
        active_problem=active,
    )


@app.route("/api/lab/run", methods=["POST"])
def api_lab_run():
    """Validate a student circuit (and optional LCD program) for a lab problem."""
    data = request.get_json(silent=True) or {}
    problem_id = str(data.get("problem_id", "p1")).strip() or "p1"
    slots = data.get("slots", [])
    program = data.get("program", "")
    if not isinstance(slots, list):
        return jsonify(
            {
                "ok": False,
                "blink": False,
                "lcd_text": "",
                "lcd_action": None,
                "message": "Invalid circuit data.",
            }
        ), 400
    if len(slots) > 8:
        return jsonify(
            {
                "ok": False,
                "blink": False,
                "lcd_text": "",
                "lcd_action": None,
                "message": "Too many parts in the circuit.",
            }
        ), 400
    if program is not None and not isinstance(program, str):
        return jsonify(
            {
                "ok": False,
                "blink": False,
                "lcd_text": "",
                "lcd_action": None,
                "message": "Invalid program data.",
            }
        ), 400
    if isinstance(program, str) and len(program) > 500:
        return jsonify(
            {
                "ok": False,
                "blink": False,
                "lcd_text": "",
                "lcd_action": None,
                "message": "Program is too long (max 500 characters).",
            }
        ), 400

    result = validate_circuit(
        problem_id,
        [str(s) for s in slots],
        program if isinstance(program, str) else "",
    )
    return jsonify(result), 200


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


def create_app() -> Flask:
    """Application factory used by tests and WSGI servers."""
    init_db()
    return app


# Ensure DB exists when loaded by gunicorn (Render) or `python app.py`
init_db()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
